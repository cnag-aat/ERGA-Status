#!/usr/bin/env perl
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Data::Dumper;
use Getopt::Long;

my $client = REST::Client->new();
$client->addHeader('Content-Type', 'application/json');
$client->addHeader('charset', 'UTF-8');
$client->addHeader('Accept', 'application/json');
$client->addHeader('Authorization' => 'Basic '.encode_base64('user1:Rd08N1Sg'));
my $erga_status_url="https://genomes.cnag.cat/erga-status/api";

my $copoclient = REST::Client->new();
$copoclient->addHeader('Content-Type', 'application/json');
$copoclient->addHeader('charset', 'UTF-8');
$copoclient->addHeader('Accept', 'application/json');
my $copo_url="https://copo-project.org/api";

my $enaclient = REST::Client->new();
$enaclient->addHeader('Content-Type', 'application/json');
$enaclient->addHeader('charset', 'UTF-8');
$enaclient->addHeader('Accept', 'application/json');
my $ena_url = "https://www.ebi.ac.uk/ena/portal/api/search";
my $usage = <<'END_HELP';
usage: $0

END_HELP
my $sample_data;
print STDERR "Ingesting data from COPO... \n";

#for my $project (qw(erga dtol)){
for my $project (qw(erga)){
  print "Searching $project in COPO...\n";
  die "No sample data!\n" unless $sample_data=(getSamples($sample_data,$project));
}
print STDERR "Done.\n";

sub getSamples {
  my $arrayref = shift;
  my $prj = shift;
  #Retrieve copo_ids from COPO for ERGA project
  $copoclient->GET("$copo_url/sample/$prj/");
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
    print STDERR "$number_found samples found for $copo_id\n";
    if ($number_found){
      my $sample_details = $response2->{data};
      foreach my $s (@$sample_details){
        # check if sample exists and update or insert.
        # need to get species using tolid_prefix or TAXON_ID
        # try to match up with collection or collection_team and set status
        print STDERR "$s->{status}\n";
        next if $s->{status} ne 'accepted';
        next if $s->{PURPOSE_OF_SPECIMEN} =~/BARCODING/;
        my $tolid = $s->{public_name};
        my $taxid = $s->{TAXON_ID};
        my $tolid_prefix = $tolid;
        $tolid_prefix =~ s/\d+$//;
        my $sample_accession = $s->{biosampleAccession};
        my $species_pk = 0;
        # CHECK for species in tracker. Skip if species not there?
        my $species_query = "$erga_status_url/species/?taxon_id=$taxid ";
        my $species_id = '';
        $client->GET($species_query);
        print STDERR "$species_query\n",$client->responseContent(),"\n";
        my $species_response = decode_json $client->responseContent();
        #print STDERR $client->responseContent();
        #print STDERR "\n$species_response\n";
        if ($species_response->{count} < 1) {
          print STDERR "Species '",$s->{SCIENTIFIC_NAME}," ($tolid_prefix:$taxid) doesn't exist. Please add first.\n";
          next;
        }else{
          my $species_url = $species_response->{results}->[0]->{url};
          my $sp_name = $species_response->{results}->[0]->{scientific_name};
          $species_url =~/(\d+)\/$/; $species_pk=$1;
          $species_id = $species_url;
          print STDERR "Found $sp_name\n Species ID: $species_id\n";
        }
        #print STDERR "building insert\n";
        #build insert
        my $record = {};
        $record->{biosampleAccession} = $sample_accession;
        $record->{tolid} = $s->{public_name};
        $record->{specimen_id} = $s->{SPECIMEN_ID};
        $record->{species} = $species_id;
        $record->{barcode} = '';
        $record->{sample_coordinator} = $s->{SAMPLE_COORDINATOR};
        # collection = models.ForeignKey(SampleCollection, on_delete=models.CASCADE, verbose_name="Collection")
        $record->{purpose_of_specimen} = $s->{PURPOSE_OF_SPECIMEN};
        $record->{gal} = $s->{GAL};
        $record->{collector_sample_id} = $s->{COLLECTOR_SAMPLE_ID};
        $record->{copo_date} = $s->{time_updated};

        print STDERR $s->{TAXON_ID},"\n";
        print STDERR $s->{SCIENTIFIC_NAME},"\n";
        print STDERR $s->{public_name},"\n";
        print STDERR $s->{SPECIMEN_ID},"\n";
        print STDERR $s->{SAMPLE_COORDINATOR},"\n";
        print STDERR $s->{PURPOSE_OF_SPECIMEN},"\n";
        print STDERR $s->{GAL},"\n";
        print STDERR $s->{COLLECTOR_SAMPLE_ID},"\n";
        print STDERR $s->{biosampleAccession},"\n";
        print STDERR $s->{time_updated},"\n";
        print STDERR $s->{status},"\n";
        print STDERR "-----------------------\n";
        #wrap it all up in JSON string
        my $insert = encode_json $record;
        # CHECK if sample exists in tracker. If so, we will PATCH. If not, POST.
        my $query = "$erga_status_url/sample/?biosampleAccession=$sample_accession ";
        #print "$query\n";
        $client->GET($query);
        my $response3 = decode_json $client->responseContent();
        if ($response3->{count} > 0) {
          #PATCH
          print STDERR "Updating existing record: \n",
            $response3 ->{results}->[0]->{url},"... \n";
          $client->PATCH($response3 ->{results}->[0]->{url}, $insert);
          #print STDERR "\nResponse:",$client->responseContent(),"\n";
        }else{
          #POST
          print STDERR "Inserting... \n";
          $client->POST("$erga_status_url/sample/", $insert);
          #print STDERR "\nResponse:",$client->responseContent(),"\n";
        }
        my $sample_collection_record = {};
        $sample_collection_record->{species} = $species_id;
        if ($s->{PURPOSE_OF_SPECIMEN} =~/REFERENCE_GENOME/){
          $sample_collection_record->{genomic_sample_status} = 'COPO';
        }
        if ($s->{PURPOSE_OF_SPECIMEN} =~/RNA_SEQUENCING/){
          $sample_collection_record->{rna_sample_status} = 'COPO';
        }
        my $status_insert = encode_json $sample_collection_record;
        my $sample_collection_query = "$erga_status_url/sample_collection/?species=".$species_pk;
        #print "$query\n";
        $client->GET($sample_collection_query);
        #print STDERR "Sample Collection Query Response:", $client->responseContent(),"\n";
        my $response4 = decode_json $client->responseContent();
        if ($response4->{count} > 0) {
          print STDERR "Updating sample collection record... ";
          $client->PATCH($response4 ->{results}->[0]->{url}, $status_insert);
          #print STDERR "\nResponse:",$client->responseContent(),"\n";
        }else{
          $client->POST("$erga_status_url/sample_collection/", $status_insert);
          #print STDERR "\nResponse:",$client->responseContent(),"\n";
        }
        #### Query the ENA for the experiment
        my $ena_query = "$ena_url/?result=read_experiment&query=sample_accession%3D%22$sample_accession%22&fields=instrument_platform%2Caccession%2Ccenter_name%2Ctax_id%2Ctissue_type%2Cstudy_title%2Cstudy_accession%2Csequencing_method%2Csample_title%2Cscientific_name%2Cproject_name%2Clibrary_strategy&format=json";
        # curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_experiment&query=sample_accession%3D%22SAMEA12832259%22&fields=accession%2Ccenter_name%2Ctax_id%2Ctissue_type%2Cstudy_title%2Cstudy_accession%2Csequencing_method%2Csample_title%2Cscientific_name%2Cproject_name%2Clibrary_strategy&format=json "https://www.ebi.ac.uk/ena/portal/api/search"
        $enaclient->GET($ena_query);
        print STDERR "ENA Response:", $enaclient->responseContent(),"\n";
        my $ena_json = $enaclient->responseContent();
        if ($ena_json){
          my $ena_response = decode_json $ena_json;
          print STDERR $ena_json,"\n";
          # {"experiment_accession":"ERX5643445","sample_accession":"SAMEA7519948","accession":"SAMEA7519948","center_name":"WELLCOME SANGER INSTITUTE","tax_id":"987985","tissue_type":"","study_title":"Mythimna impura (smoky wainscot), genomic and transcriptomic data","study_accession":"PRJEB42100","sequencing_method":"","sample_title":"61d718a7-c047-4973-8f59-97c8067c9bfc-dtol","scientific_name":"Mythimna impura","project_name":"DTOL","library_strategy":"WGS"}
        }
        #exit;
      }
    }
  }
  return 1;
}
