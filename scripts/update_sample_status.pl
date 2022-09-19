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
$client->addHeader('Authorization' => 'Basic '.encode_base64('erga-test1:Rd08N1Sg'));
my $erga_status_url="https://genomes.cnag.cat/erga-status/api";

my $copoclient = REST::Client->new();
$copoclient->addHeader('Content-Type', 'application/json');
$copoclient->addHeader('charset', 'UTF-8');
$copoclient->addHeader('Accept', 'application/json');
my $copo_url="https://copo-project.org/api";
#### EXAMPLE TABLES ####

#assemblies.csv
#tolid_prefix,description,type,span,contig_n50,scaffold_n50,chromosome_level,percent_placed,busco,busco_db,busco_version,qv
#odPhaVent,ratatosk.nextdenovo.hypo1.purged,Primary,207000000,2400000,6900000,FALSE,0,C:80.5%[S:78.4%;D:2.1%];F:8.5%;M:11.0%;n:954,metazoa_odb10,4.0.6,32.3
#ilHelHell,nextdenovo.assembly.hypo1.purged.curated,Primary,547306268,23624374,23624374,TRUE,100,C:98.0%[S:97.7%;D:0.3%];F:0.7%;M:1.3%;n:1013,arthropoda_odb10,4.0.6,46.6

my $usage = <<'END_HELP';
usage: $0


END_HELP
my $assembly_data;
#$assembly_csv_file = shift or print $usage and exit;
die "No sample data!\n" unless $sample_data=(getSamples($sample_data));
print STDERR "Parsed data from COPO... ready to update ERGA-Status.\n";
print STDERR "Updating...\n"; #print STDERR Data::Dumper->Dump($assembly_data),"\n" and exit;
#update_sample_status($sample_data);

sub add_assembly_project{
  my $assemblies = shift;
  for (my $i = 0;$i<@$assemblies; $i++){
    my $tolid_prefix=$assemblies->[$i]->{'tolid_prefix'};
    print STDERR "$tolid_prefix ",$assemblies->[$i]->{description},"\n";
    my $qv_rounded = sprintf("%.2f",$assemblies->[$i]->{qv});
    print STDERR $assemblies->[$i]->{qv},"\n";
    $assemblies->[$i]->{qv} = $qv_rounded ;
    my $pp_rounded = sprintf("%.1f",$assemblies->[$i]->{percent_placed});
    $assemblies->[$i]->{percent_placed} = $pp_rounded;

    #Retrieve species from target species table
    $client->GET("$erga_status_url/species/?tolid_prefix=". $tolid_prefix);
    my $response1 = decode_json $client->responseContent();
    my $species_url = $response1->{results}->[0]->{url};
    $species_url =~/(\d+)\/$/;
    my $species_id = $1;

    #Retrieve project based on species_id
    $client->GET("$erga_status_url/assembly_project/?species=". $species_id);
    my $response2 = decode_json $client->responseContent();
    #print STDERR $client->responseContent() and exit;
    my $project_url = $response2->{results}->[0]->{url};
    $project_url =~/(\d+)\/$/;
    #print STDERR "$project_url\n";
    my $project_id = $1;

    if ($response2->{count} == 1) { #proceed if there is one and only one project
      $assemblies->[$i]->{project}=$project_id;
      my $d=$assemblies->[$i]->{description};
      my $cn50=$assemblies->[$i]->{contig_n50};
      my $sn50=$assemblies->[$i]->{scaffold_n50};
      my $busco=$assemblies->[$i]->{busco};
      my $busco_db=$assemblies->[$i]->{busco_db};
      my $busco_version=$assemblies->[$i]->{busco_version};
      my $qv=$assemblies->[$i]->{qv};

      #Get the busco_db. If it doesn't exist, add it via the admin interface and redo this. In future, we can do it here.
      $client->GET("$erga_status_url/busco_db/?db=". $busco_db);
      my $busco_db_response = decode_json $client->responseContent();
      my $busco_db_url = $busco_db_response->{results}->[0]->{url};

      #Get the BUSCO version. If it doesn't exist, add it via the admin interface and redo this. In future, we can do it here.
      $client->GET("$erga_status_url/busco_version/?species=". $busco_version);
      my $buso_version_response = decode_json $client->responseContent();
      my $busco_version_url = $busco_version_response->{results}->[0]->{url};

      #check to see if the assembly already exists. Give warning.
      my $query = "$erga_status_url/assembly/?project=$project_id&description=$d&contig_n50=$cn50&scaffold_n50=$sn50&qv=$qv";
      #print "$query\n";
      $client->GET($query);
      my $response3 = decode_json $client->responseContent();
      if ($response3->{count} > 0) {
        print STDERR "Possible duplicate: $d\n",encode_json($response3),"\nAdding anyway. You may want to manually remove this record.\n";
      }
      #Replace regular strings with REST URLs.
      $assemblies->[$i]->{project}=$project_url;
      $assemblies->[$i]->{busco_db}=$busco_db_url;
      $assemblies->[$i]->{busco_version}=$busco_version_url;

      #wrap it all up in JSON string
      my $insert = encode_json $assemblies->[$i];
      #print STDERR "$insert\n";
      $client->POST("$erga_status_url/assembly/", $insert);
      print STDERR "Inserting... Response:",$client->responseContent(),"\n";
    } else {
      print STDERR "Couldn't find project. Please add project for $tolid_prefix via the admin interface. Skipping for now.\n"; #print STDERR "Project could not be found in the samples table. Please add sample first.\n",encode_json($response2),"\n";
    }
  }
  return 1;
}

sub getSamples {
  my $arrayref = shift;
  #Retrieve copo_ids from COPO for ERGA project
  $copoclient->GET("$copo_url/sample/erga/");
  #print $copoclient->responseContent()."\n";
  my $response1 = decode_json $copoclient->responseContent();
  print STDERR "$response1\n";
  print STDERR $response1->{data},"\n";
  my $sample_array = $response1->{data};
  foreach my $record (@$sample_array){
    my $copo_id = $record->{copo_id};
    print STDERR "$copo_id\n";
    $copoclient->GET("$copo_url/sample/copo_id/$copo_id/");
    my $response2 = decode_json $copoclient->responseContent();
    print STDERR "$response2\n";
    my $number_found = $response2->{number_found};
    print STDERR "$number_found\n";
    if ($number_found){
      my $sample_details = $response2->{data};
      foreach my $s (@$sample_details){
        # check if sample exists and update or insert.
        # need to get species using tolid_prefix or TAXON_ID
        # try to match up with collection or collection_team and set status
        next if $s->{status} ne 'accepted';
        next if $s->{PURPOSE_OF_SPECIMEN} =~/BARCODING/;
        my $tolid = $s->{public_name};
        my $tolid_prefix = $tolid;
        $tolid_prefix =~ s/\d+$//;
        my $sample_accession = $s->{biosampleAccession};

        # CHECK for species in tracker. Skip of species not there?
        my $species_query = "$erga_status_url/species/?tolid_prefix=$tolid_prefix ";
        #print "$query\n";
        my $species_id = '';
        $client->GET($species_query);
        my $response4 = decode_json $client->responseContent();
        if ($response4->{count} < 1) {
          print STDERR "Species doesn't exist. Please add first.\n";
          next;
        }else{
          my $species_url = $response1->{results}->[0]->{url};
          $species_url =~/(\d+)\/$/;
          $species_id = $1;
        }

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
          print STDERR "Updating existing record... ";
          $client->PATCH("$erga_status_url/sample/", $insert);
          print STDERR "\nResponse:",$client->responseContent(),"\n";
        }else{
          #POST
          print STDERR "Inserting... ";
          $client->POST("$erga_status_url/sample/", $insert);
          print STDERR "\nResponse:",$client->responseContent(),"\n";
        }



      }
    }

  }
  return 1;
  # my @h = split ",",$head;
  # my $count=0;
  # while (my $record = <TAB>) {
  #   chomp $record;
  #   my @r = split ",",$record;
  #
  #   for (my $i=0;$i<@h; $i++) {
  #     $arrayref->[$count]->{$h[$i]}=($r[$i]);
  #   }
  #   $count++;
  # }

  #return $count?$arrayref:0;
}
