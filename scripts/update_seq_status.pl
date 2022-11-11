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

my $enaclient = REST::Client->new();
$enaclient->addHeader('Content-Type', 'application/json');
$enaclient->addHeader('charset', 'UTF-8');
$enaclient->addHeader('Accept', 'application/json');
my $ena_url = "https://www.ebi.ac.uk/ena/portal/api/search";
my $usage = <<'END_HELP';
usage: $0

END_HELP

#library_strategy Hi-C, WGS, RNA-Seq,
#Instrument_platform OXFORD_NANOPORE PACBIO_SMRT ILLUMINA
my $sample_accession = shift @ARGV;

#### Query the ENA for the experiment
my $ena_query = "$ena_url/?result=read_experiment&query=sample_accession%3D%22$sample_accession%22&fields=instrument_platform%2Caccession%2Ccenter_name%2Ctax_id%2Ctissue_type%2Cstudy_title%2Cstudy_accession%2Csequencing_method%2Csample_title%2Cscientific_name%2Cproject_name%2Clibrary_strategy&format=json";
# curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_experiment&query=sample_accession%3D%22SAMEA12832259%22&fields=accession%2Ccenter_name%2Ctax_id%2Ctissue_type%2Cstudy_title%2Cstudy_accession%2Csequencing_method%2Csample_title%2Cscientific_name%2Cproject_name%2Clibrary_strategy&format=json "https://www.ebi.ac.uk/ena/portal/api/search"
$enaclient->GET($ena_query);
#print STDERR "ENA Response:", $enaclient->responseContent(),"\n";
my $ena_json = $enaclient->responseContent();
if ($ena_json){
  my $ena_response = decode_json $ena_json;
  #print Data::Dumper->Dump([$ena_response]);
  my $number_found = scalar @$ena_response;
  print STDERR "$number_found runs found for $sample_accession\n";
  if ($number_found){
    foreach my $r (@$ena_response){
      my $proj_url = '';
      my $species_query = "$erga_status_url/species/?taxon_id=".$r->{tax_id};
      print STDERR $species_query,"\n";
      $client->GET($species_query);
      my $species_response = decode_json $client->responseContent();
      my $species_url = $species_response->{results}->[0]->{url};
      print STDERR $species_url and exit;
      my $sequencing_query = "$erga_status_url/species/?species=".$species_url;
      print STDERR $sequencing_query,"\n";
      $client->GET($sequencing_query);
      my $sequencing_response = decode_json $client->responseContent();
      my $sequencing_url = $sequencing_response->{results}->[0]->{url};
      print STDERR $species_url and exit;
      print STDERR $r->{instrument_platform},"\t",$r->{library_strategy},"\n";
      my $reads_record = {};
      $reads_record->{ont_ena} = $study_accession if $r->{instrument_platform} eq 'OXFORD_NANOPORE';
      $reads_record->{hifi_ena} = $study_accession if $r->{instrument_platform} eq 'PACBIO_SMRT';
      $reads_record->{short_ena} = $study_accession if $r->{instrument_platform} eq 'ILLUMINA' and $r->{library_strategy} eq 'WGS';
      $reads_record->{rnaseq_ena} = $study_accession if $r->{instrument_platform} eq 'ILLUMINA' and $r->{library_strategy} eq 'RNA-Seq';
      $reads_record->{hic_ena} = $study_accession if $r->{instrument_platform} eq 'ILLUMINA' and $r->{library_strategy} eq 'Hi-C';
      my $insert = encode_json $reads_record;
      my $reads_query = "$erga_status_url/reads/?project=$proj_url";
      #print "$query\n";
      $client->GET($reads_query);
      my $reads_response = decode_json $client->responseContent();
      if ($reads_response->{count} > 0) {
        #PATCH
        print STDERR "Updating existing record: \n",
        $reads_response->{results}->[0]->{url},"... \n";
        $client->PATCH($reads_response->{results}->[0]->{url}, $insert);
        #print STDERR "\nResponse:",$client->responseContent(),"\n";
      }else{
        #POST
        print STDERR "Inserting... \n";
        $client->POST("$erga_status_url/reads/", $insert);
        #print STDERR "\nResponse:",$client->responseContent(),"\n";
      }
      # genomic_seq_status = models.CharField(max_length=12, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
      #   hic_seq_status = models.CharField(max_length=12, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
      #   rna_seq_status = models.CharField(max_length=12, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
      #
    }
  }
  # {"experiment_accession":"ERX5643445","sample_accession":"SAMEA7519948","accession":"SAMEA7519948","center_name":"WELLCOME SANGER INSTITUTE","tax_id":"987985","tissue_type":"","study_title":"Mythimna impura (smoky wainscot), genomic and transcriptomic data","study_accession":"PRJEB42100","sequencing_method":"","sample_title":"61d718a7-c047-4973-8f59-97c8067c9bfc-dtol","scientific_name":"Mythimna impura","project_name":"DTOL","library_strategy":"WGS"}
}
