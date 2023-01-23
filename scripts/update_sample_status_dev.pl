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
$client->addHeader('Authorization' => 'Basic '.encode_base64('dev-admin:8ek$Ytco8blx'));
my $erga_status_url="https://genomes.cnag.cat/erga-stream-dev/api";

my $copoclient = REST::Client->new();
$copoclient->addHeader('Content-Type', 'application/json');
$copoclient->addHeader('charset', 'UTF-8');
$copoclient->addHeader('Accept', 'application/json');
my $copo_url="https://copo-project.org/api";

my $usage = <<'END_HELP';
usage: $0

END_HELP
my $sample_data;
print STDERR "Ingesting data from COPO... \n";
die "No sample data!\n" unless $sample_data=(getSamples($sample_data));
print STDERR "Done.\n";

sub getSamples {
  my $arrayref = shift;
  #Retrieve copo_ids from COPO for ERGA project
  $copoclient->GET("$copo_url/sample/erga/");
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
        my $tolid_prefix = $tolid;
        $tolid_prefix =~ s/\d+$//;
        my $sample_accession = $s->{biosampleAccession};
        my $species_pk = 0;
        # CHECK for species in tracker. Skip if species not there?
        my $species_query = "$erga_status_url/species/?tolid_prefix=$tolid_prefix ";
        my $species_id = '';
        $client->GET($species_query);
        my $species_response = decode_json $client->responseContent();
        print STDERR $client->responseContent();
        print STDERR "\n$species_response\n";
        if ($species_response->{count} < 1) {
          print STDERR "Species '",$s->{SCIENTIFIC_NAME}," ($tolid_prefix) doesn't exist. Please add first.\n";
          next;
        }else{
          my $species_url = $species_response->{results}->[0]->{url};
          $species_url =~/(\d+)\/$/; $species_pk=$1;
          $species_id = $species_url;
          print STDERR "Species ID: $species_id\n";
        }
        print STDERR "building insert\n";
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
          $sample_collection_record->{genomic_sample_status} = 'Submitted';
        }
        if ($s->{PURPOSE_OF_SPECIMEN} =~/RNA_SEQUENCING/){
          $sample_collection_record->{rna_sample_status} = 'Submitted';
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
  return 1;
}
