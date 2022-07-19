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

#print STDERR Data::Dumper->Dump([$assembly_data->[0]]);

#print STDERR $assembly_data->[0]->{project},"\n";
add_assembly($assembly_data);
#die "Failed adding assembly!\n" unless
sub add_assembly{
  my $assemblies = shift;
  for (my $i = 0;$i<@$assemblies; $i++){
    my $tolid_prefix=$assemblies->[$i]->{'tolid_prefix'};
    #print STDERR Data::Dumper->Dump([$a]);
    print STDERR "$tolid_prefix ",$assemblies->[$i]->{description},"\n";
    #exit;
    my $qv_rounded = sprintf("%.2f",$assemblies->[$i]->{qv});
    print STDERR $assemblies->[$i]->{qv},"\n";
    $assemblies->[$i]->{qv} = $qv_rounded ;
    my $pp_rounded = sprintf("%.1f",$assemblies->[$i]->{percent_placed});
    $assemblies->[$i]->{percent_placed} = $pp_rounded;
    $client->GET("$url/species/?tolid_prefix=". $tolid_prefix);
    #print STDERR  $client->responseContent(),"\n";
    my $response1 = decode_json $client->responseContent();
    #print STDERR Data::Dumper->Dump([$response1]);
    my $species_url = $response1->{results}->[0]->{url};
    $species_url =~/(\d+)\/$/;
    my $species_id = $1;
    #print STDERR "$species_url\n";
    #print STDERR "$species_id\n";
    #print STDERR $assembly_data->[0]->{sample},"\n";
    $client->GET("$url/assembly_project/?species=". $species_id);
    my $response2 = decode_json $client->responseContent();
    #print STDERR $client->responseContent() and exit;
    my $project_url = $response2->{results}->[0]->{url};
    $project_url =~/(\d+)\/$/;
    print STDERR "$project_url\n";
    my $project_id = $1;

    if ($response2->{count} == 1) {
      $assemblies->[$i]->{project}=$project_id;
      my $d=$assemblies->[$i]->{description};
      my $cn50=$assemblies->[$i]->{contig_n50};
      my $sn50=$assemblies->[$i]->{scaffold_n50};
      my $busco=$assemblies->[$i]->{busco};
      my $busco_db=$assemblies->[$i]->{busco_db};
      my $busco_version=$assemblies->[$i]->{busco_version};
      my $qv=$assemblies->[$i]->{qv};

      $client->GET("$url/busco_db/?db=". $busco_db);
      my $busco_db_response = decode_json $client->responseContent();
      my $busco_db_url = $busco_db_response->{results}->[0]->{url};
      $client->GET("$url/busco_version/?species=". $busco_version);
      my $buso_version_response = decode_json $client->responseContent();
      my $busco_version_url = $busco_version_response->{results}->[0]->{url};
      my $query = "$url/assembly/?project=$project_id&description=$d&contig_n50=$cn50&scaffold_n50=$sn50&qv=$qv";
      print "$query\n";
      $client->GET("$url/assembly/?project=$project_id&description=$d&contig_n50=$cn50&scaffold_n50=$sn50&qv=$qv");
      my $response3 = decode_json $client->responseContent();
      if ($response3->{count} > 0) {
        print STDERR "Possible duplicate: $d\n",encode_json($response3),"\nAdding anyway. You may want to manually remove this record.\n";
      }
      $assemblies->[$i]->{project}=$project_url;
      $assemblies->[$i]->{busco_db}=$busco_db_url;
      $assemblies->[$i]->{busco_version}=$busco_version_url;
      my $insert = encode_json $assemblies->[$i];
      print STDERR "$insert\n";
      $client->POST("$url/assembly/", $insert);
      print STDERR "Inserted:\n",$client->responseContent(),"\n";
    } else {
      print STDERR "couldn't find project. please add project for $tolid_prefix. Skipping for now.\n"; #print STDERR "Project could not be found in the samples table. Please add sample first.\n",encode_json($response2),"\n";
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
  my @h = split ",",$head;
  my $count=0;
  while (my $record = <TAB>) {
    chomp $record;
    #print STDERR "$record\n";
    my @r = split ",",$record;

    for (my $i=0;$i<@h; $i++) {
      #print STDERR $h[$i],"\n";
      #$h[$i]=~s/sample_barcode/sample/; #fix some field names on the fly. later we should fix the flatfiles.
      $arrayref->[$count]->{$h[$i]}=($r[$i]);
    }
    $count++;
  }
  close TAB;
  return $count?$arrayref:0;
}
