#!/usr/bin/env perl
#use lib '/home/devel/talioto/perl5/lib/perl5/';
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
my $url="https://genomes.cnag.cat/erga-status/api";

#### EXAMPLE TABLES ####

#assemblies.tsv
#Assembly project	Description	Type	Assembly span	Contig N50	Scaffold N50	Chr level	% placed	BUSCO	BUSCO db	BUSCO version	QV
#odPhaVent	ratatosk.nextdenovo.hypo1.purged	Pseudohaploid Primary	207000000	2400000	6900000		0.0	"C:80.5%[S:78.4%	D:2.1%]	F:8.5%M:11.0%	n:954"	metazoa_odb10	4.0.6	32.30
#ilHelHell	nextdenovo.assembly.hypo1.purged.curated	Pseudohaploid Primary	547306268	23624374	23624374	true	100	"C:98.0%[S:97.7%,D:0.3%],F:0.7%,M:1.3%,n:1013"	arthropoda_odb10	4.0.6	46.6
#rPodLil	flye.nextpolish_superreads.purgedups.10X.YaHS	Pseudohaploid Primary	1460245709	1478291	89641981	true	98.2	"C:95.9%[S:94.6%,D:1.3%],F:1.4%,M:2.7%,n:3354"	vertebrata_odb10	4.0.6	40.36

my $usage = "usage: $0 assemblies.tsv\n";
# GetOptions(
# 	   'bc:s'      => \$bc,
# 	   'v:s'  => \$version
# 	  );
# die $usage if !($bc && $version);
#my $updateAnnotation = 0;
my $assembly_data;
my $assembly_tsv_file = shift;

die "No assembly data" unless $assembly_data=(loadTbl($assembly_tsv_file,$assembly_data));

print STDERR "Parsed data files... ready to add to ERGA-Status.\n";
print STDERR "Adding assembly data...\n"; #print STDERR Data::Dumper->Dump($assembly_data),"\n" and exit;
die "Failed adding assembly!\n" unless add_assembly();


sub add_assembly{
  my $qv_rounded = sprintf("%.2f",$assembly_data->[0]->{qv});
  my $pp_rounded = sprintf("%.1f",$assembly_data->[0]->{percent_placed});
  $client->GET("$url/assemblies/?assembly=". $assembly_data->[0]->{assembly});
  print STDERR  $client->responseContent(),"\n";
  my $response1 = decode_json $client->responseContent();
  print STDERR $assembly_data->[0]->{sample},"\n";
  $client->GET("$url/sample/?barcode=". $assembly_data->[0]->{sample});
  my $response2 = decode_json $client->responseContent();
  if ($response2->{count} == 1) {
    $assembly_data->[0]->{sample}=$response2->{results}->[0]->{url};
  } else {
    print STDERR "Sample $bc could not be found in the samples table. Please add sample first.\n",encode_json($response2),"\n";
    return;
  }
  if ($response1->{count} == 1) {
    print STDERR $assembly_data->[0]->{assembly}," is already in database:\n",encode_json($response1),"\nWill update with new data..\n";
    my $insert = encode_json $assembly_data->[0];
    my $record_to_update = $response1->{results}->[0]->{url}; #the URL;
    print STDERR "Deleting $record_to_update\n"; # and exit;
    $client->DELETE($record_to_update);
    print STDERR "Deleted record:\n",$client->responseContent(),"\n";
    my $insert = encode_json $assembly_data->[0];
    $client->POST("$url/assembly/", $insert);
    print STDERR "Inserted new record:\n",$client->responseContent(),"\n";
    return 1;
  } elsif ($response1->{count} > 1) {
    print STDERR "Multiple records match ", $assembly_data->[0]->{assembly},":\n";
    foreach my $r (@{$response1->{results}}) {
      print STDERR $r->{url},"\n";
      die "Exiting.\n";
    }
  } else {
    my $insert = encode_json $assembly_data->[0];
    $client->POST("$url/assembly/", $insert);
    print STDERR "Inserted:\n",$client->responseContent(),"\n";
    return 1;
  }
}


sub loadTbl {
  my $file =  shift;
  my $arrayref = shift;
  open TAB, "<$file" or die "couldn't open $file\n";
  my $head = <TAB>;
  chomp $head;
  my @h = split "\t",$head;
  my $count=0;
  while (my $record = <TAB>) {
    chomp $record;
    my @r = split "\t",$record;

    for (my $i=0;$i<@h; $i++) {
      #$h[$i]=~s/sample_barcode/sample/; #fix some field names on the fly. later we should fix the flatfiles.
      $arrayref->[$count]->{lc($h[$i])}=($r[$i]);
    }
    $count++;
  }
  close TAB;
  return $count?$arrayref:0;
}
