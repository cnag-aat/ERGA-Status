#!/usr/bin/env perl
use lib "/home/groups/assembly/talioto/myperlmods/";
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Data::Dumper;
use Getopt::Long;
my $conf = ".ergastream.cnf";
my $erga_status_url="https://genomes.cnag.cat/erga-stream/api";
my $printhelp = 0;
GetOptions(
	   'c|config:s' => \$conf,
     'h|help' => \$printhelp
	  );
my $usage = <<'END_HELP';
usage: update_sequencing.pl [-c <ergastream.cnf>] [-h] 
 
  The ergastream configuration file (default name: ".ergastream.cnf") has the format:
    URL https://genomes.cnag.cat/erga-stream/api
    username  <username>
    password  <password>

  If using the development server or the URL changes at any time, you can replace the URL.
  The username and passwords are the ones assigned to your team. If you'd like to use one attached to an email, 
  let Tyler know and he will grant your registered user the same priveleges.

END_HELP

if ($printhelp){
  print $usage;
}
open(CONF,"<$conf") or die "Configuration file $conf does not exist. Please create it in the current working directory or specify the path to it using the -c option.";
my %config = ();
while(my $l = <CONF>){
  chomp $l;
  my ($k,$v)=split(/\s+/,$l);
  $config{$k}=$v;
}
if(exists $config{'URL'}){
  $erga_status_url=$config{'URL'}
}
die "please provide username in conf file" if (! exists($config{'username'}));
die "please provide password in conf file" if (!exists($config{'password'}));
my $client = REST::Client->new();
$client->addHeader('Content-Type', 'application/json');
$client->addHeader('charset', 'UTF-8');
$client->addHeader('Accept', 'application/json');
$client->addHeader('Authorization' => 'Basic '.encode_base64($config{'username'}.":".$config{'password'}));
#my $erga_status_url="https://genomes.cnag.cat/erga-stream-dev/api";


my $copoclient = REST::Client->new();
$copoclient->addHeader('Content-Type', 'application/json');
$copoclient->addHeader('charset', 'UTF-8');
$copoclient->addHeader('Accept', 'application/json');
my $copo_url="https://copo-project.org/api";

my $usage = <<'END_HELP';
usage: $0

END_HELP
my $all_species_query = "$erga_status_url/species/";
$client->GET($all_species_query);
#print $client->responseContent() and exit;
my $response = decode_json $client->responseContent();
my %taxids = ();
if ($response->{count} > 0){
  foreach my $sp (@{$response->{results}}){
    if ($sp->{taxon_id} =~ /\d/){$taxids{$sp->{taxon_id}}++;}
    print "taxon_id: $sp->{taxon_id}\n";
  }
}
print scalar %taxids," found\n";
foreach my $k (sort keys %taxids){print STDERR "$k\n";} 
my $sample_data;
print STDERR "Ingesting ERGA data from COPO... \n";
die "No sample data!\n" unless $sample_data=(getSamples($sample_data, 'sample/erga/'));
print STDERR "Done.\n";

print STDERR "Ingesting ERGA-BGE data from COPO... \n";
die "No sample data!\n" unless $sample_data=(getSamples($sample_data, 'sample/associated_tol_project/BGE-ERGA/'));
print STDERR "Done.\n";

sub getSamples {
  my $arrayref = shift;
  my $project_sub_url = shift;
  #Retrieve copo_ids from COPO for ERGA project
  $copoclient->GET("$copo_url/$project_sub_url");
  my $response1 = decode_json $copoclient->responseContent();
  #print STDERR "$response1\n";
  #print STDERR $response1->{data},"\n";
  my $sample_array = $response1->{data};
  foreach my $record (@$sample_array){
    my $copo_id = $record->{copo_id};
    print STDERR "COPO ID: $copo_id\n";
    $copoclient->GET("$copo_url/sample/copo_id/$copo_id/");
    my $response2 = decode_json $copoclient->responseContent();
    #print STDERR "$response2\n";
    my $number_found = $response2->{number_found};
    #print STDERR "$number_found samples found for $copo_id\n";
    if ($number_found){
      my $sample_details = $response2->{data};
      foreach my $s (@$sample_details){
        # check if sample exists and update or insert.
        # need to get species using tolid_prefix or TAXON_ID
        # try to match up with collection or collection_team and set status
        #print STDERR "$s->{status}\n";
        my $tolid = $s->{public_name};
        my $taxid = $s->{TAXON_ID};
        print Data::Dumper->Dump([$response2]) if exists $taxids{$taxid};
        #exit if $taxid == 1457099;
        next if !($s->{status} eq 'accepted' || $s->{status} eq 'pending');
        next if $s->{PURPOSE_OF_SPECIMEN} =~/BARCODING/;
        next if !exists $taxids{$taxid};
        my $tolid_prefix = $tolid;
        $tolid_prefix =~ s/\d+$//;
        my $sample_accession = $s->{biosampleAccession};
        my $copo_id = $s->{copo_id};
        my $species_pk = 0;
        # CHECK for species in tracker. Skip if species not there?
        my $species_query = "$erga_status_url/species/?taxon_id=$taxid";
        my $species_id = '';
        $client->GET($species_query);
        print STDERR $species_query,"\n",$client->responseContent(),"\n\n";
        my $species_response = decode_json $client->responseContent();
        #print STDERR "\n$species_response\n";
        if ($species_response->{count} < 1) {
          #print STDERR "Species '",$s->{SCIENTIFIC_NAME}," ($tolid_prefix) doesn't exist. Please add first.\n";
          next;
        }elsif ($species_response->{count} == 1){
          my $species_url = $species_response->{results}->[0]->{url};
          $species_url =~/(\d+)\/$/; $species_pk=$1;
          $species_id = $species_url;
          print STDERR "Species ID: $species_id\n";
          
          #print STDERR "building insert\n";
          #build insert

    # specimen_id = models.CharField(max_length=20, help_text='Internal Specimen ID')
    # species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="species",null=True, blank=True)
    # #barcode = models.CharField(max_length=20, help_text='Tube barcode')
    # tolid = models.CharField(max_length=20, help_text='Registered ToLID for the Specimen', null=True, blank=True)
    # collection = models.ForeignKey(SampleCollection, on_delete=models.CASCADE, verbose_name="Collection")
    # sample_coordinator = models.CharField(max_length=50, help_text='Sample coordinator', null=True, blank=True)
    # tissue_removed_for_biobanking = models.BooleanField(default=False)
    # tissue_voucher_id_for_biobanking = models.CharField(max_length=50, null=True, blank=True)
    # tissue_for_biobanking = models.CharField(max_length=50, null=True, blank=True)
    # dna_removed_for_biobanking = models.BooleanField(default=False)
    # dna_voucher_id_for_biobanking = models.CharField(max_length=50, null=True, blank=True)
    # voucher_id = models.CharField(max_length=50, help_text='Voucher ID', null=True, blank=True)
    # proxy_voucher_id = models.CharField(max_length=50, help_text='Proxy voucher ID', null=True, blank=True)
    # voucher_link = models.CharField(max_length=200, null=True, blank=True)
    # proxy_voucher_link = models.CharField(max_length=200, null=True, blank=True)
    # voucher_institution = models.CharField(max_length=200, null=True, blank=True)
    # biobanking_team = models.ForeignKey(BiobankingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="biobanking team")
          my $sample_collection_q = "$erga_status_url/sample_collection/?species=".$species_pk;
          my $scurl = '';
          $client->GET($sample_collection_q);
          my $sc_response = decode_json $client->responseContent();
          if ($sc_response->{count} > 0) {
            $scurl = $sc_response->{results}->[0]->{url};
          }
          print STDERR $s->{TAXON_ID},"\n";
          print STDERR $s->{SCIENTIFIC_NAME},"\n";
          print STDERR $s->{public_name},"\n";
          print STDERR $s->{SPECIMEN_ID},"\n";
          my $specimen_record = {};

          $specimen_record->{specimen_id} = $s->{SPECIMEN_ID};
          $specimen_record->{tolid} = $s->{public_name};
          $specimen_record->{sample_coordinator} = $s->{SAMPLE_COORDINATOR};
          $specimen_record->{species} = $species_id;
          $specimen_record->{collection} = $scurl;
          $specimen_record->{tissue_removed_for_biobanking} = $s->{TISSUE_REMOVED_FOR_BIOBANKING};
          $specimen_record->{tissue_voucher_id_for_biobanking} = $s->{TISSUE_VOUCHER_ID_FOR_BIOBANKING};
          $specimen_record->{tissue_for_biobanking} = $s->{TISSUE_FOR_BIOBANKING};
          $specimen_record->{dna_removed_for_biobanking} = $s->{DNA_REMOVED_FOR_BIOBANKING};
          $specimen_record->{dna_voucher_id_for_biobanking} = $s->{DNA_VOUCHER_ID_FOR_BIOBANKING};
          $specimen_record->{voucher_id}  = $s->{VOUCHER_ID};
          $specimen_record->{proxy_voucher_id}  = $s->{PROXY_VOUCHER_ID};
          $specimen_record->{voucher_link} = $s->{VOUCHER_LINK};
          $specimen_record->{proxy_voucher_link} = $s->{PROXY_VOUCHER_LINK};
          $specimen_record->{voucher_institution} = $s->{VOUCHER_INSTITUTION};
          my $specimen_url = '';
          my $specimen_insert = encode_json $specimen_record;
          my $tid = $specimen_record->{tolid};
          # CHECK if speciment exists in tracker. If so, we will PATCH. If not, POST.
          my $specimen_query = "$erga_status_url/specimen/?tolid=$tid";
          #print "$query\n";
          $client->GET($specimen_query);
          print $client->responseContent(),"\n";
          my $specimen_response = decode_json $client->responseContent();
          if ($specimen_response->{count} > 0) {
            #PATCH
            print STDERR "Updating existing record: ",
            $specimen_url = $specimen_response->{results}->[0]->{url};
            $client->PATCH($specimen_url, $specimen_insert);
            print STDERR "\nResponse:",$client->responseContent(),"\n";
          }else{
            #POST
            print STDERR "Inserting... ";
            $client->POST("$erga_status_url/specimen/", $specimen_insert);
            my $specimen_insert_response = decode_json  $client->responseContent();
            $specimen_url = $specimen_insert_response->{results}->[0]->{url};
            #print STDERR "\nResponse:",$client->responseContent(),"\n" and exit;
          }
          $client->GET($specimen_query);
          my $specimen_response2 = decode_json $client->responseContent();
          $specimen_url = $specimen_response2->{results}->[0]->{url};

          my $record = {};
          $record->{copo_id} = $copo_id;
          $record->{biosampleAccession} = $sample_accession;
          $record->{species} = $species_id;
          $record->{barcode} = '';
          # collection = models.ForeignKey(SampleCollection, on_delete=models.CASCADE, verbose_name="Collection")
          $record->{gal} = $s->{GAL};
          $record->{collector_sample_id} = $s->{COLLECTOR_SAMPLE_ID};
          $record->{copo_date} = $s->{time_updated};
          $record->{purpose_of_specimen} = $s->{PURPOSE_OF_SPECIMEN};
          $record->{tube_or_well_id} = $s->{TUBE_OR_WELL_ID};
          $record->{specimen} = $specimen_url;


          #wrap it all up in JSON string
          my $insert = encode_json $record;
          # CHECK if sample exists in tracker. If so, we will PATCH. If not, POST.
          #my $query = "$erga_status_url/sample/?biosampleAccession=$sample_accession ";
          my $query = "$erga_status_url/sample/?copo_id=$copo_id ";
          print "$query\n";
          $client->GET($query);
          print STDERR $client->responseContent(),"\n";
          my $response3 = decode_json $client->responseContent();
          if ($response3->{count} > 0) {
            #PATCH
            print STDERR "Updating existing record: ",
              $response3 ->{results}->[0]->{url},"... \n";
            $client->PATCH($response3 ->{results}->[0]->{url}, $insert);
            print STDERR "\nResponse:",$client->responseContent(),"\n";
          }else{
            #POST
            print STDERR "Inserting... ";
            $client->POST("$erga_status_url/sample/", $insert);
            print STDERR "\nResponse:",$client->responseContent(),"\n";
          }
          my $sample_collection_record = {};
          $sample_collection_record->{species} = $species_id;
          if ($s->{PURPOSE_OF_SPECIMEN} =~/REFERENCE_GENOME/){
            if ($s->{status} eq 'pending'){
              $sample_collection_record->{genomic_sample_status} = 'Pending';
            }else{
              $sample_collection_record->{genomic_sample_status} = 'Submitted';
            }
          }
          if ($s->{PURPOSE_OF_SPECIMEN} =~/RNA_SEQUENCING/){
            if ($s->{status} eq 'pending'){
              $sample_collection_record->{rna_sample_status} = 'Pending';
            }else{
              $sample_collection_record->{rna_sample_status} = 'Submitted';
            }
          }
          my $status_insert = encode_json $sample_collection_record;
          my $sample_collection_query = "$erga_status_url/sample_collection/?species=".$species_pk;
          #print "$query\n";
          $client->GET($sample_collection_query);
          print STDERR "Sample Collection Query Response:", $client->responseContent(),"\n";
          my $response4 = decode_json $client->responseContent();
          if ($response4->{count} > 0) {
            print STDERR "Updating sample collection record... ";
            $client->PATCH($response4 ->{results}->[0]->{url}, $status_insert);
            print STDERR "\nResponse:",$client->responseContent(),"\n";
          }else{
            $client->POST("$erga_status_url/sample_collection/", $status_insert);
            print STDERR "\nResponse:",$client->responseContent(),"\n";
          }
        }
      }
    }
  }
  return 1;
}
