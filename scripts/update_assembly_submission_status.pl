#!/usr/bin/env perl
use strict;
use lib "/home/groups/assembly/talioto/myperlmods/";
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Data::Dumper;
use Getopt::Long;
use File::Basename;
use Cwd qw(cwd);
no warnings 'utf8';

my $conf = ".ergastream.cnf";
my $erga_status_url="https://genomes.cnag.cat/erga-stream/api";
my $printhelp = 0;
my $seq_data;
my $sequencing_tsv_file = 0;
my $verbose = 0;
my $deploy = 0;
GetOptions(
    'c|config:s' => \$conf,
    'h|help' => \$printhelp,
    'v|verbose' => \$verbose
);

my $usage = <<'END_HELP';
usage: update_assembly_submission_status.pl [-c <gtc-assembly.cnf>] [-h] 
 
  The configuration file (default name: "credentials.cnf") has the format:
    URL http://http://172.16.10.22/lims/api/seq
    username  <username>
    password  <password>

END_HELP
#   tolid_prefix  scientific_name genomic_seq_status  hic_seq_status  rna_seq_status  note  recipe  ont_yield hifi_yield  hic_yield short_yield rnaseq_pe

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
  $erga_status_url=$config{'URL'};
}
die "please provide username in conf file" if (! exists($config{'username'}));
die "please provide password in conf file" if (!exists($config{'password'}));

my $client = REST::Client->new();
$client->addHeader('Content-Type', 'application/json');
$client->addHeader('charset', 'UTF-8');
$client->addHeader('Accept', 'application/json');
$client->addHeader('Authorization' => 'Basic '.encode_base64($config{'username'}.":".$config{'password'}));

open (ENA, 'curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "result=assembly&query=study_tree(PRJEB61747)&fields=assembly_title%2Cassembly_level%2Cassembly_name%2Cassembly_quality%2Cassembly_type%2Cbase_count%2Cassembly_accession%2Cversion%2Ccenter_name%2Ccompleteness_score%2Ccontamination_score%2Ccommon_name%2Cdescription%2Csample_accession%2Crun_accession%2Cscientific_name%2Cstudy_accession%2Csub_species%2Ctaxonomic_classification%2Ctax_id%2Clast_updated&format=tsv" "https://www.ebi.ac.uk/ena/portal/api/search" |');
my $header = <ENA>;
chomp $header;
my @fnames = split "\t",$header;
#print @fnames;
my $assemblies;
my $c = 0;
while (my $line = <ENA>){
  chomp $line;
  my @f = split "\t",$line;
  #my %assembly;
  for (my $i = 0; $i<@f; $i++){
    #print $fnames[$i],"\n";
    $assemblies->[$c]->{$fnames[$i]} = $f[$i];
  }
  #push @assemblies, \%assembly;
  $c++;
}
close ENA;
print Data::Dumper->Dump([$assemblies]) if $verbose; 
my %taxids;
my %projects;
foreach my $a (@$assemblies){
  my %record = %$a;
  #print STDERR $record{'tax_id'},"\n";
  $taxids{$record{'tax_id'}}=1;
  #print %record;
}
foreach my $taxid (keys %taxids){
  #update status as submitted
  my $response = make_request($client,"$erga_status_url/species/?taxon_id=". $taxid);
  next if $response->{count} != 1;
  #print Data::Dumper->Dump([$response]);
  my $species_url = $response->{results}->[0]->{url};
  $species_url =~/(\d+)\/$/;
  my $species_id = $1;
  print "taxid: $taxid species_id: $species_id\n";

  my $project_resp = make_request($client,"$erga_status_url/assembly_project/?species=". $species_id);
  my $project_url = $project_resp->{results}->[0]->{url};
  $projects{$taxid}=$project_url; 
  $project_url =~/(\d+)\/$/;
  my $project_id = $1;
  my %assembly_status_insert_data = ();
  $assembly_status_insert_data{status}='Submitted';
  make_patch($client,$project_url, encode_json \%assembly_status_insert_data );

}

# ASSEMBLY_TYPE_CHOICES = (
#     ('Primary', 'Pseudohaploid Primary'),
#     ('Alternate', 'Pseudohaploid Alternate'),
#     ('Hap1', 'Phased Haplotype 1'),
#     ('Hap2', 'Phased Haplotype 2'),
#     ('Maternal', 'Trio-phased Maternal'),
#     ('Paternal', 'Trio-phased Paternal'),
#     ('MT', 'Mitogenome'),
#     ('Chloroplast', 'Chloroplast'),
#     ('Endosymbiont', 'Endosymbiont')
# )

foreach my $a (@$assemblies){
  #next if not $deploy;
  my %record = %$a;
  #print Data::Dumper->Dump([%record]) if $verbose;
  #print STDERR $record{'tax_id'},"\n";
  my $gca = $record{'accession'};
  #print "GCA: $gca\n";
  my $ver = $record{'version'};
  my $chr_level = 0;
  $chr_level = 1 if $record{'assembly_level'} =~ /chromosome/;
  my $type = 'Primary';
  $type = 'Alternate' if $record{'assembly_name'} =~ /alternate/i;
  $type = 'Alternate' if $record{'assembly_title'} =~ /alternate/i;
  $type = 'Endosymbiont' if $record{'assembly_name'} =~ /(co|sym)biont/i;
  $type = 'Endosymbiont' if $record{'assembly_title'} =~ /(co|sym)biont/i;
  next if $type ne 'Primary';
  my $assembly_insert = '';
  #contruct insert
  my %assembly_insert_data = ();
  my $gca_ver = "$gca.$ver";
  if ($gca_ver =~/GCA/){
    print "datasets summary genome accession $gca_ver\n" if $verbose;
    my $assembly_summary_json = `datasets summary genome accession $gca_ver`;
    print STDERR $assembly_summary_json,"\n" if $verbose;
    #contig_n50
    #scaffold_n50
    my $summary_data = decode_json $assembly_summary_json;
    #print STDERR Data::Dumper->Dump([$summary_data]) if $verbose; 
    if ($summary_data->{total_count} == 1){
      $assembly_insert_data{contig_n50}=$summary_data->{reports}->[0]->{assembly_stats}->{contig_n50};
      $assembly_insert_data{scaffold_n50}=$summary_data->{reports}->[0]->{assembly_stats}->{scaffold_n50},"\n";
    }
    #exit;
  }

  $assembly_insert_data{project}=$projects{$record{'tax_id'}};
  $assembly_insert_data{type}=$type;
  $assembly_insert_data{chromosome_level}=$chr_level;
  $assembly_insert_data{span}=$record{'base_count'};
  $assembly_insert_data{last_updated}=$record{'last_updated'};
  #$assembly_insert_data{description}=$record{'assembly_name'}." ".$record{'assembly_title'};
  $assembly_insert_data{description}=$record{'assembly_title'};
  $assembly_insert_data{gca}=$record{'accession'};
  $assembly_insert_data{version}=$record{'version'};
  $assembly_insert_data{accession}=$record{'study_accession'};



  #######
  my $assembly_resp = make_request($client,"$erga_status_url/assembly/?gca=$gca" );
  # if records exist, if version is the same, don't do anything
  # if version is higher, patch the record with new values
  if ($assembly_resp->{count} > 0) {
  #PATCH
  #if ($assembly_resp->{results}->[0]->{version} < $ver){
    print STDERR "Updating existing assembly record: \n" if $verbose;
    my $assembly_url = $assembly_resp->{results}->[0]->{url};
    make_patch($client,$assembly_url, encode_json \%assembly_insert_data);
  #}
}else{
  #POST
  print STDERR "Inserting new assembly data... \n" if $verbose;
  make_post($client,"$erga_status_url/assembly/", encode_json \%assembly_insert_data);
}
  #print %record;
}
sub make_request{
  my $client= shift;
  my $query = shift;
  print STDERR "$query\n" if $verbose;
  my $response = "";
    for (my $i=0; $i<10; $i++){
      $client->GET($query);
      $response = $client->responseContent();
      print STDERR "$response\n" if $verbose;
      last if $response !~ /timeout/;
      sleep 1;
    }
    if ($response =~ /timeout/){
      return 0;
    }elsif ($response =~ /<html/){
      print STDERR "$response\n";
      return 0;
    }else{

      print STDERR "$response\n" if $verbose;
      return decode_json $response;
    }
}
sub make_patch{
  my $client= shift;
  my $url = shift;
  my $insert = shift;
  print STDERR "$url\n$insert\n" if $verbose;
  my $response = "";
    for (my $i=0; $i<10; $i++){
      $client->PATCH($url,$insert);
      $response = $client->responseContent();
      print STDERR "$response\n" if $verbose;
      last if $response !~ /timeout/;
      sleep 1;
    }
    if ($response =~ /timeout/){
      return 0;
    }elsif ($response =~ /<html/){
      print STDERR "$response\n";
      return 0;
    }else{
      return decode_json $response;
    }
}
sub make_post{
  my $client= shift;
  my $url = shift;
  my $insert = shift;
  print STDERR "$url\n$insert\n" if $verbose;
  my $response = "";
    for (my $i=0; $i<10; $i++){
      $client->POST($url,$insert);
      $response = $client->responseContent();
      print STDERR "$response\n" if $verbose;
      last if $response !~ /timeout/;
      sleep 1;
    }
    if ($response =~ /timeout/){
      return 0;
    }elsif ($response =~ /<html/){
      print STDERR "$response\n";
      return 0;
    }elsif ($response =~ /Error/){
      print STDERR "$response\n";
      return 0;
    }else{
      return decode_json $response;
    }
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
    next if $record !~ /\w/;
    my @r = split /[\t]/,$record;
    for (my $i=0;$i<@h; $i++) {
      $arrayref->[$count]->{$h[$i]}=($r[$i]);
    }
    $count++;
  }
  close TAB;
  return $count?$arrayref:0;
}
