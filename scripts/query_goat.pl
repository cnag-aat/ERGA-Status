#!/usr/bin/env perl
use lib "/home/www/resistome.cnag.cat/erga-dev/scripts/";
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Data::Dumper;
use Getopt::Long;
#use LWP::Protocol::http;
$ENV{PERL_LWP_SSL_VERIFY_HOSTNAME}=0;

my $goatclient = REST::Client->new();
$goatclient->addHeader('Content-Type', 'application/json');
$goatclient->addHeader('charset', 'UTF-8');
$goatclient->addHeader('Accept', 'application/json');
my $goat_url="https://goat.genomehubs.org/api/v2/";
my $taxid_query = 0;
my $printhelp = 0;
GetOptions(
	   'taxon_id|taxid:s' => \$taxid_query,
     'h|help' => \$printhelp
	  );

#print join("\t",qw(original_species tags taxon_id kingdom phylum class order family genus scientific_name tolid_prefix chromosome_number haploid_number ploidy c_value genome_size common_name synonym goat_target_list_status goat_sequencing_status )),"\n";
print join("\t",qw(original_species tags taxon_id kingdom phylum class order family genus scientific_name tolid_prefix chromosome_number haploid_number ploidy c_value genome_size common_name synonym )),"\n";

  $goatclient->GET("$goat_url"."record?recordId=$taxid_query&result=taxon&taxonomy=ncbi");
  my $goatresponse2 = decode_json $goatclient->responseContent();
  #print Data::Dumper->Dump([$goatresponse2]) and exit;
  die $goatresponse2->{status}->{hits}. " records\n" if $goatresponse2->{status}->{hits}!=1;
  my $record = $goatresponse2->{records}->[0]->{record};
  #print Data::Dumper->Dump([$record]);
  my $tags = "";
  my %out;
  $out{'taxon_id'}=$taxid_query;
  $out{'scientific_name'}=$record->{'scientific_name'};
  $out{'chromosome_number'}=$record->{attributes}->{'chromosome_number'}->{'value'};
  $out{'haploid_number'}=$record->{attributes}->{'haploid_number'}->{'value'};
  $out{'c_value'}=$record->{attributes}->{'c_value'}->{'value'};
  $out{'genome_size'}=$record->{attributes}->{'genome_size'}->{'value'};
  $out{'ploidy'}=$record->{attributes}->{'ploidy'}->{'value'};

  $out{'common_name'}=exists($record->{attributes}->{'common_name'})?$record->{attributes}->{'common_name'}->{'value'}:'';
  $out{'synonym'}=exists($record->{attributes}->{'synonym'})?$record->{attributes}->{'synonym'}->{'value'}:'';
  $out{'goat_list_status'} = 'none';
  foreach my $v (@{$record->{attributes}->{'other_priority'}->{'values'}}){
    if ($v->{'value'} eq 'ERGA-BGE'){
      $out{'goat_list_status'} = 'other_priority';
    }
  }
  foreach my $v (@{$record->{attributes}->{'family_representative'}->{'values'}}){
    if ($v->{'value'} eq 'ERGA-BGE'){
      $out{'goat_list_status'} = 'family_representative';
    }
  }
  $out{'goat_sequencing_status'} = $record->{attributes}->{'sequencing_status_erga-bge'}->{'value'};
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
      (
      $out{'scientific_name'},
      $tags,
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
      $out{'synonym'},
      #$out{'goat_list_status'},
      #$out{'goat_sequencing_status'}
      )
    ),"\n";

