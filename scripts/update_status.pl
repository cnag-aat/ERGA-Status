#!/usr/bin/env perl
use lib "/home/groups/assembly/talioto/myperlmods/"; #change this to point to your PERL5LIB module directory or set the $PERL5LIB environment variable
#use lib '/home/groups/assembly/talioto/erga_scripts';
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Getopt::Long;
use strict;

# https://metacpan.org/pod/REST::Client
# https://metacpan.org/pod/JSON::PP
# https://metacpan.org/pod/MIME::Base64
# https://anaconda.org/bioconda/perl-rest-client
# https://anaconda.org/bioconda/perl-json-pp
# https://anaconda.org/bioconda/perl-mime-base64

my $conf = ".ergastream.cnf";
my $erga_status_url="https://genomes.cnag.cat/erga-stream/api";
my $printhelp = 0;
my $seq_data;
my $sequencing_tsv_file = 0;
my %SEQUENCING_STATUS_CHOICES = (
  'Waiting'=>1,
  'Received'=>1,
  'Extracted'=>1,
  'Sequencing'=>1,
  'TopUp'=>1,
  'External'=>1,
  'Submitted'=>1,
  'Done'=>1,
  'Issue'=>1
);

GetOptions(
  'c|config:s' => \$conf,
  'f|file:s' => \$sequencing_tsv_file,
  'h|help' => \$printhelp
);
my $usage = <<'END_HELP';
usage: update_sequencing.pl [-h] [-c <ergastream.cnf>] -f <sequencing_status_update.tsv>
 
  The ergastream configuration file (default name: ".ergastream.cnf") has the format:
    URL https://genomes.cnag.cat/erga-stream/api
    username  <username>
    password  <password>

  If using the development server or the URL changes at any time, you can replace the URL.
  The username and passwords are the ones assigned to your team. If you'd like to use one attached to an email, 
  let Tyler know and he will grant your registered user the same priveleges.

  sequencing_status_update.tsv has the following tab-delimited columns:
    center
    scientific_name (one or the other of scientific_name or tolid_prefix is required)
    tolid_prefix (one or the other of scientific_name or tolid_prefix is required)
    recipe
    instrument
    library_strategy
    status
    notes (optional)

  recipe choices: 
    'ONT60','HIFI25'
  instrument_model choices: 
    'Illumina NovaSeq 6000', 'PromethION', 'GridION', https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html#permitted-values-for-instrument
  library_strategy choices: 
    'WGS', 'Hi-C', 'RNA-Seq'
  status choices: 
    'Waiting','Received','Extracted','Sequencing','TopUp','External','Done','Submitted','Issue'
END_HELP

if ($printhelp or !$sequencing_tsv_file){
  print $usage and exit;
}
open(CONF,"<$conf") or die "Configuration file $conf does not exist. Please create it in the current working directory or specify the path to it using the -c option.";
my %config = ();
while(my $l = <CONF>){
  chomp $l;
  my ($k,$v)=split(/\s+/,$l);
  $config{$k}=$v;
}
if(exists $config{'URL'}){
  $erga_status_url=$config{'URL'};
}
die "please provide username in conf file" if (! exists($config{'username'}));
die "please provide password in conf file" if (!exists($config{'password'}));
die "No seq data!\n" unless $seq_data=(loadTbl($sequencing_tsv_file,$seq_data));
print STDERR "Parsed data files... now updating ERGA-Stream.\n";
my $client = REST::Client->new();
$client->addHeader('Content-Type', 'application/json');
$client->addHeader('charset', 'UTF-8');
$client->addHeader('Accept', 'application/json');
$client->addHeader('Authorization' => 'Basic '.encode_base64($config{'username'}.":".$config{'password'}));
update($seq_data,$erga_status_url);

sub update{
  my $sequpdate= shift;
  my $erga_status_url = shift;
  my $read_type = "";
  for (my $i = 0;$i<@$sequpdate; $i++){
    my $tolid_prefix=$sequpdate->[$i]->{'tolid_prefix'};
    my $scientific_name=$sequpdate->[$i]->{'scientific_name'};
    my $instrument=$sequpdate->[$i]->{'instrument'};
    my $library_strategy=$sequpdate->[$i]->{'library_strategy'};
    my $out_library_strategy = "WGS";
    if ($library_strategy =~ /RNA-?Seq/i){$read_type = "RNA";$library_strategy = "RNA-Seq";}
    if ($instrument =~ /^Illumina/i && $library_strategy =~  /WGS/i){$read_type = "Illumina";$library_strategy = "WGS";}
    if ($instrument =~ /(PacBio|Revio|Sequel)/i  && $library_strategy =~ /WGS/i){$read_type = "HiFi";$library_strategy = "WGS";}
    if ($instrument =~ /^Illumina/i && $library_strategy =~ /Hi-?C/i){$read_type = "HiC";$library_strategy = "Hi-C";}
    if ($instrument =~ /ION$/i && $library_strategy =~ /WGS/i){$read_type = "ONT";$library_strategy = "WGS";}
    my $yield=$sequpdate->[$i]->{'yield'};
    my $status = $sequpdate->[$i]->{status};
    #print STDERR "\n$read_type\t$library_strategy\t$status\n\n";

    my $species_id = 0;
    my $species_url = 0;
    if ($tolid_prefix =~m/\w/){
      #Retrieve species from target species table
      $client->GET("$erga_status_url/species/?tolid_prefix=". $tolid_prefix);
      my $response1 = decode_json $client->responseContent();
      $species_url = $response1->{results}->[0]->{url};
      $species_url =~/(\d+)\/$/;
      $species_id = $1;
    }elsif($scientific_name =~m/\w/){
      #Retrieve species from target species table
      $client->GET("$erga_status_url/species/?scientific_name=". $scientific_name);
      my $response1 = decode_json $client->responseContent();
      $species_url = $response1->{results}->[0]->{url};
      $species_url =~/(\d+)\/$/;
      $species_id = $1;
    }else{die "please provide tolid or scientific_name\n"}

    #Retrieve project based on species_id
    $client->GET("$erga_status_url/sequencing/?species=". $species_id);
    my $response2 = decode_json $client->responseContent();
    my $project_url = $response2->{results}->[0]->{url};
    $project_url =~/(\d+)\/$/;
    my $project_id = $1;
    #print STDERR "\n$project_url\n";
    if ($response2->{count} == 1) { #proceed if there is one and only one project
      $sequpdate->[$i]->{project}=$project_id;
      #my $status=$sequpdate->[$i]->{status};
      if (($status =~/\S/) && ! exists $SEQUENCING_STATUS_CHOICES{$status}){
        die "Status must be one of: ".join(", ",sort keys %SEQUENCING_STATUS_CHOICES)."\n";
      }
      my $note=$sequpdate->[$i]->{notes};
      my $recipe=$sequpdate->[$i]->{recipe};
      if ($status =~/\S/){
        $client->GET("$erga_status_url/recipe/?name=". $recipe);
        my $recipe_response = decode_json $client->responseContent();
        my $recipe_url = $recipe_response->{results}->[0]->{url};
        my %seq_insert_data = ();
        $seq_insert_data{species}=$species_url;
        $seq_insert_data{long_seq_status}=$status if $read_type =~/(HiFi|ONT)/i;
        $seq_insert_data{short_seq_status}=$status if $read_type =~/Illumina/i;
        $seq_insert_data{hic_seq_status}=$status if $read_type =~/HiC/i;
        $seq_insert_data{rna_seq_status}=$status if $read_type =~/RNA/i;
        if ($note =~/\S/){
          my $shortened_note = substr( $note, 0, 300 );
          $seq_insert_data{note}=$shortened_note; 
        }
        $seq_insert_data{recipe}=$recipe if $recipe =~/\S/;
        my $seqinsert = encode_json \%seq_insert_data;
        #print STDERR "$seqinsert\n";
        print STDERR "Updating $project_url\n";
        $client->PATCH($project_url, $seqinsert);
        #print STDERR $client->responseContent(),"\n";
      }
    } else {
      print STDERR "Couldn't find project. Please add project for $scientific_name $tolid_prefix via the admin interface. Skipping for now.\n"; 
    }
  }
  return 1;
}

sub loadTbl {
  my $file =  shift;
  my $arrayref = shift;
  open TAB, "<$file" or die "couldn't open $file\n";
  my $head = <TAB>;
  chomp $head;
  my @h = split /[\t]/,$head;
  my $count=0;
  while (my $record = <TAB>) {
    chomp $record;
    my @r = split /[\t]/,$record;
    for (my $i=0;$i<@h; $i++) {
      $arrayref->[$count]->{$h[$i]}=($r[$i]);
    }
    $count++;
  }
  close TAB;
  return $count?$arrayref:0;
}
