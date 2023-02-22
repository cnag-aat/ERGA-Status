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

my $goatclient = REST::Client->new();
$goatclient->addHeader('Content-Type', 'application/json');
$goatclient->addHeader('charset', 'UTF-8');
$goatclient->addHeader('Accept', 'application/json');
my $goat_url="https://goat.genomehubs.org/api/v2/";
my $usage = <<'END_HELP';
usage: $0 <species_list.tsv>

END_HELP
open SPECIES, "<$ARGV[0]";
my $tags = "erga_long";
if (exists $ARGV[1]){
  $tags = $ARGV[1] or "erga_long";
}
print join("\t",qw(tags taxon_id kingdom phylum class order family genus scientific_name tolid_prefix chromosome_number haploid_number ploidy c_value genome_size common_name synonym)),"\n";
while (my $line = <SPECIES>){
  chomp $line;
  my @species_data = split "\t",$line;
  print STDERR "Looking up $species_data[0] in GoaT... \n";
  print STDERR "$species_data[0] not found! Skipping...\n" unless getSpecies(\@species_data);
}

sub getSpecies {
  my $arrayref = shift;
  my @species_data = @$arrayref;
  my $speciesquery = $species_data[0];
  my $space = '%20';
  $speciesquery=~s/ /$space/g;
  my $query = "$goat_url"."lookup?searchTerm=$speciesquery&result=taxon&size=10&taxonomy=ncbi&suggestSize=3&gramSize=3&maxErrors=3&confidence=1&indent=4";
  $goatclient->GET("$goat_url"."lookup?searchTerm=$speciesquery&result=taxon&size=10&taxonomy=ncbi&suggestSize=3&gramSize=3&maxErrors=3&confidence=1&indent=4");
  my $goatresponse1 = decode_json $goatclient->responseContent();
  my $species_array = $goatresponse1->{results};
  my $num_hits = $goatresponse1->{status}->{hits};
  if (!$num_hits){print STDERR $species_data[0]," not found. Skipping...\n"; return 0;}
  my $taxid = $species_array->[0]->{result}->{taxon_id};
  print STDERR "Fetching taxid:$taxid from GoaT\n";# and exit;
  if ($taxid=~/^[\d]*$/){
    $goatclient->GET("$goat_url"."record?recordId=$taxid&result=taxon&taxonomy=ncbi");
    my $goatresponse2 = decode_json $goatclient->responseContent();
    #print Data::Dumper->Dump([$goatresponse2]) and exit;
    my $record = $goatresponse2->{records}->[0]->{record};
    #print Data::Dumper->Dump([$record]);
    my %out;
    $out{'taxon_id'}=$taxid;
    $out{'scientific_name'}=$record->{'scientific_name'};
    $out{'chromosome_number'}=$record->{attributes}->{'chromosome_number'}->{'value'};
    $out{'haploid_number'}=$record->{attributes}->{'haploid_number'}->{'value'};
    $out{'c_value'}=$record->{attributes}->{'c_value'}->{'value'};
    $out{'genome_size'}=$record->{attributes}->{'genome_size'}->{'value'};
    $out{'ploidy'}=$record->{attributes}->{'ploidy'}->{'value'};

    $out{'common_name'}=exists($record->{attributes}->{'common_name'})?$record->{attributes}->{'common_name'}->{'value'}:'';
    $out{'synonym'}=exists($record->{attributes}->{'synonym'})?$record->{attributes}->{'synonym'}->{'value'}:'';
    foreach my $taxrec (@{$record->{'taxon_names'}}){
      $out{'tolid_prefix'} = $taxrec->{'name'} if $taxrec->{'class'} eq 'tolid_prefix';
    }
    foreach my $lin (@{$record->{'lineage'}}){
      $out{'kingdom'} = $lin->{'scientific_name'} if $lin->{'taxon_rank'} eq 'kingdom';
      $out{'phylum'} = $lin->{'scientific_name'} if $lin->{'taxon_rank'} eq 'phylum';
      $out{'class'} = $lin->{'scientific_name'} if $lin->{'taxon_rank'} eq 'class';
      $out{'order'} = $lin->{'scientific_name'} if $lin->{'taxon_rank'} eq 'order';
      $out{'family'} = $lin->{'scientific_name'} if $lin->{'taxon_rank'} eq 'family';
      $out{'genus'} = $lin->{'scientific_name'} if $lin->{'taxon_rank'} eq 'genus';
    }
    print join(
      "\t",
        ($tags,
        $out{'taxon_id'},
        $out{'kingdom'},
        $out{'phylum'},
        $out{'class'},
        $out{'order'},
        $out{'family'},
        $out{'genus'},
        $out{'scientific_name'},
        $out{'tolid_prefix'},
        $out{'chromosome_number'},
        $out{'haploid_number'},
        $out{'ploidy'},
        $out{'c_value'},
        $out{'genome_size'},
        $out{'common_name'},
        $out{'synonym'}
        )
      ),"\n";
  }

  return 1;
}
