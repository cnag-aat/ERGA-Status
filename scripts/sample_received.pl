#!/usr/bin/env perl
use lib "/home/groups/assembly/talioto/myperlmods/";
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Data::Dumper;
use Getopt::Long;
my $lconf = "/home/groups/assembly/talioto/erga_scripts/cnag-lims.cnf";
my $lims_url="https://lims.cnag.cat/lims/api/seq";
my $printhelp = 0;
my $econf = "/home/groups/assembly/talioto/erga_scripts/ergastream-sequencing.cnf";
my $erga_status_url="https://genomes.cnag.cat/erga-stream/api";

GetOptions(
	   'limsconf:s' => \$lconf,
	   'ergaconf:s' => \$econf,
     'h|help' => \$printhelp,
	  );

my $args = 'project=1323';
my $usage = <<'END_HELP';
usage: update_sequencing.pl [-c <cnag-lims.cnf>] [-h] 
 
  The configuration file (default name: "credentials.cnf") has the format:
    URL http://http://172.16.10.22/lims/api/seq
    username  <username>
    password  <password>

END_HELP
#   tolid_prefix  scientific_name genomic_seq_status  hic_seq_status  rna_seq_status  note  recipe  ont_yield hifi_yield  hic_yield short_yield rnaseq_pe

if ($printhelp){
  print $usage;
}

#####################
# CNAG LIMS         #
#####################
open(LIMSCONF,"<$lconf") or die "Configuration file $lconf does not exist. Please create it in the current working directory or specify the path to it using the -c option.";
my %lconfig = ();
while(my $l = <LIMSCONF>){
  chomp $l;
  my ($k,$v)=split(/\s+/,$l);
  $lconfig{$k}=$v;
}
if(exists $lconfig{'URL'}){
  $lims_url=$lconfig{'URL'}
}
die "please provide username in limsconf file" if (! exists($lconfig{'username'}));
die "please provide password in limsconf file" if (!exists($lconfig{'password'}));
my $std_args = "format=json&limit=0&username=".$lconfig{'username'}."&api_key=".$lconfig{'password'};

my $limsclient = REST::Client->new();

#####################
# ERGA-STREAM       #
#####################
open(ERGACONF,"<$econf") or die "Configuration file $econf does not exist. Please create it in the current working directory or specify the path to it using the -c option.";
my %econfig = ();
while(my $l = <ERGACONF>){
  chomp $l;
  my ($k,$v)=split(/\s+/,$l);
  $econfig{$k}=$v;
}
if(exists $econfig{'URL'}){
  $ergastatus_url=$econfig{'URL'}
}
die "please provide username in ergaconf file" if (! exists($econfig{'username'}));
die "please provide password in ergaconf file" if (!exists($econfig{'password'}));

my $ergaclient = REST::Client->new();
$ergaclient->addHeader('Content-Type', 'application/json');
$ergaclient->addHeader('charset', 'UTF-8');
$ergaclient->addHeader('Accept', 'application/json');
$ergaclient->addHeader('Authorization' => 'Basic '.encode_base64($econfig{'username'}.":".$econfig{'password'}));


#https://lims.cnag.cat/lims/api/seq/primarymaterial/
#all_available_material_used
#date_received
#barcode
my $usage = <<'END_HELP';
usage: $0

END_HELP
#my $query = "$lims_url/flowcell_lane_index/?format=json&limit=0&library__subprojects__subproject_name=ERGA_01";
#print STDERR "Connecting to $lims_url\n";
#my $query = "$lims_url/subproject/";
my %update = ();
my $endpoint = 'primarymaterial';
print STDERR "connecting to $lims_url/$endpoint/?$std_args\n";
#$client->GET("$lims_url/$endpoint/?$std_args&$args");
$limsclient->GET("$lims_url/$endpoint/?$std_args");
#exit;
my $response = decode_json $limsclient->responseContent();
print STDERR "Found $response->{meta}->{total_count} records\n";
my $records = $response->{objects};
foreach my $r (@$records){
  my $tube_or_well_id = "";
  if ($r->{barcode}){
    $tube_or_well_id = $r->{barcode};
    my $day = $r->{date_received};
    $day =~s/T.*//;
    print STDERR $r->{barcode},"\t",$tube_or_well_id,"\t",$day,"\n";
    #construct insert
    my $record->{date_received} = $day;
    my $insert = encode_json $record;
    print STDERR "$insert\n";
    my $query = "$erga_status_url/sample/?tube_or_well_id=$tube_or_well_id ";
    print "$query\n";
    $ergaclient->GET($query);
    print STDERR $ergaclient->responseContent(),"\n";
    my $sample_response = decode_json $ergaclient->responseContent();
    if ($sample_response->{count} > 0) {
      #PATCH
      print STDERR "Updating existing record: ", $sample_response ->{results}->[0]->{url},"... \n";
      $ergaclient->PATCH($sample_response ->{results}->[0]->{url}, $insert);
      print STDERR "\nResponse:",$ergaclient->responseContent(),"\n";
    }else{
      print STDERR "sample wiith tube_or_well_id=$sample_tube_or_well_id doesn't exist. Skipping...\n";
    }
  }
}
