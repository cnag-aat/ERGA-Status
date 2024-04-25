#!/usr/bin/env perl
use lib "/home/groups/assembly/talioto/myperlmods/";
use lib "/home/groups/assembly/talioto/erga_scripts/";
use LWP::Protocol::https;
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Data::Dumper;
use Getopt::Long;
use utf8;
#binmode(STDOUT, ":encoding(UTF-8)");
#binmode(STDERR, ":encoding(UTF-8)");

use Unicode::Normalize;
#use Text::Unidecode;
#use warnings;
#use warnings qw( FATAL utf8 );
my $conf = ".ergastream.cnf";
my $erga_status_url="https://genomes.cnag.cat/erga-stream/api";
my $printhelp = 0;
my $taxid = 0;
my $verbose = 0;
GetOptions(
	   'c|config:s' => \$conf,
     'h|help' => \$printhelp,
     'taxid:s' => \$mytaxid,
     'verbose|v' => \$verbose
	  );
my $usage = <<'END_HELP';
usage: update_sequencing.pl [-c <ergastream.cnf>] [-h] 
 
  The ergastream configuration file (default name: ".ergastream.cnf") has the format:
    URL https://genomes.cnag.cat/erga-stream/api
    username  <username>
    password  <password>

  If using the development server or the URL changes at any time, you can replace the URL.
  The username and passwords are the ones assigned to your team. If you'd like to use one attached to an email, 
  let Tyler know and he will grant your registered user the same priveleges.

END_HELP

if ($printhelp){
  print $usage;
}
open(CONF,"<$conf") or die "Configuration file $conf does not exist. Please create it in the current working directory or specify the path to it using the -c option.";
my %config = ();
while(my $l = <CONF>){
  chomp $l;
  if (length($l)){
    my ($k,$v)=split(/\s+/,$l);
    $config{$k}=$v;
  }
}
if(exists $config{'URL'}){
  $erga_status_url=$config{'URL'}
}
die "please provide username in conf file" if (! exists($config{'username'}));
die "please provide password in conf file" if (!exists($config{'password'}));
my $client = REST::Client->new();
$client->addHeader('Content-Type', 'application/json');
$client->addHeader('charset', 'UTF-8');
$client->addHeader('Accept', 'application/json');
$client->addHeader('Authorization' => 'Basic '.encode_base64($config{'username'}.":".$config{'password'}));
$client->setTimeout(10);
#my $erga_status_url="https://genomes.cnag.cat/erga-stream-dev/api";


my $copoclient = REST::Client->new();
$copoclient->setTimeout(30);
$copoclient->addHeader('Content-Type', 'application/json');
$copoclient->addHeader('charset', 'UTF-8');
$copoclient->addHeader('Accept', 'application/json');
my $copo_url="https://copo-project.org/api";

my $all_species_query = "$erga_status_url/species/";
$client->GET($all_species_query);
#print $client->responseContent() if $verbose;# and exit;
my $response = decode_json $client->responseContent();
my %taxids = ();
my @taxonid_list = ();
if ($response->{count} > 0){
  foreach my $sp (@{$response->{results}}){
    if (defined $sp->{taxon_id} and ($sp->{taxon_id} =~ /\d/)){
      if ($mytaxid){ next if $sp->{taxon_id} ne $mytaxid;}
      $taxids{$sp->{taxon_id}}++;
      push @taxonid_list,$sp->{taxon_id};
      print "taxon_id: $sp->{taxon_id}\n" if $verbose;
    }
  }
}
print scalar %taxids," found\n";
if ($verbose){
  foreach my $k (sort keys %taxids){print STDERR "$k\n";}     
}
my $sample_data;
my %bestcopostatus = ();
my %bestcopostatusrna = ();
print STDERR "Ingesting ERGA-BGE data from COPO... \n";

foreach my $taxid (@taxonid_list){
  getSamples($taxid);
}
sub getSamples {
  my $tid = shift;
  #my $project_sub_url = shift;
  #Retrieve copo_ids from COPO for ERGA project
  $copoclient->GET("$copo_url/sample/sample_field/TAXON_ID/$tid");
  #print STDERR $copoclient->responseContent(),"\n" if $verbose;
  my $response1 = decode_json $copoclient->responseContent();
  my $sample_array = $response1->{data};
  foreach my $record (@$sample_array){
    my $copo_id = $record->{copo_id};
    print STDERR "COPO ID: $copo_id\n" if $verbose;
    $copoclient->GET("$copo_url/sample/copo_id/$copo_id/");
    print STDERR $copoclient->responseContent(),"\n" if $verbose;
    my $response2 = decode_json($copoclient->responseContent());
    my $number_found = $response2->{number_found};
    if ($number_found){
      my $sample_details = $response2->{data};
      foreach my $s (@$sample_details){
        # check if sample exists and update or insert.
        # need to get species using tolid_prefix or TAXON_ID
        # try to match up with collection or collection_team and set status
        my $tolid = $s->{public_name};
        my $taxid = $s->{TAXON_ID};
        my $tol_project = $s->{tol_project};
        my $associated_tol_project = $s->{associated_tol_project};
        if (!(($tol_project=~/ERGA/)||($tol_project=~/BGE/)||($associated_tol_project=~/ERGA/)||($associated_tol_project=~/BGE/))){
          next;
        }else{print STDERR $s->{public_name},"|",$s->{copo_id},"\n";}
        if ($s->{status} =~/pending/){$s->{status}='pending';}
        next if $s->{PURPOSE_OF_SPECIMEN} =~/BARCODING/;
        next if !exists $taxids{$taxid};
        my $tolid_prefix = $tolid;
        $tolid_prefix =~ s/\d+$//;
        my $sample_accession = $s->{biosampleAccession};
        my $copo_id = $s->{copo_id};
        my $species_pk = 0;
        # CHECK for species in tracker. Skip if species not there?
        my $species_query = "$erga_status_url/species/?taxon_id=$taxid";
        my $species_id = '';
        my $species_response = make_request ($client,$species_query);

        if ($species_response->{count} < 1) {
          next;
        }elsif ($species_response->{count} == 1){
          my $species_url = $species_response->{results}->[0]->{url};
          $species_url =~/(\d+)\/$/; $species_pk=$1;
          $species_id = $species_url;
          print STDERR "$tolid_prefix: $species_id\n" if $verbose;
          if ($species_response->{results}->[0]->{tolid_prefix} !~/\S/){
            make_patch($client,$species_id, encode_json {'tolid_prefix'=>$tolid_prefix});    
          }
          my $decomposed = NFKD( $s->{GAL} );
          $decomposed =~ s/\p{NonspacingMark}//g;
          my $seqteam_q = "$erga_status_url/sequencing_team/?gal_name=".$decomposed;
          my $seqteam_url = '';
          my $seqteam_response = make_request($client,$seqteam_q);

          if ($seqteam_response->{count} > 0) {
            $seqteam_url = $seqteam_response->{results}->[0]->{url};
          }

          my $sample_collection_q = "$erga_status_url/sample_collection/?species=".$species_pk;
          my $scurl = '';
          my $sc_response = make_request($client,$sample_collection_q);

          if ($sc_response->{count} > 0) {
            $scurl = $sc_response->{results}->[0]->{url};
          }
          my $specimen_record = {};
          $specimen_record->{specimen_id} = $s->{SPECIMEN_ID};
          $specimen_record->{tolid} = $s->{public_name};
          $specimen_record->{species} = $species_id;
          $specimen_record->{collection} = $scurl;
          $specimen_record->{tissue_removed_for_biobanking} = $s->{TISSUE_REMOVED_FOR_BIOBANKING};
          $specimen_record->{tissue_voucher_id_for_biobanking} = $s->{TISSUE_VOUCHER_ID_FOR_BIOBANKING};
          $specimen_record->{proxy_tissue_voucher_id_for_biobanking} = $s->{PROXY_TISSUE_VOUCHER_ID_FOR_BIOBANKING};
          $specimen_record->{tissue_for_biobanking} = $s->{TISSUE_FOR_BIOBANKING};
          $specimen_record->{dna_removed_for_biobanking} = $s->{DNA_REMOVED_FOR_BIOBANKING};
          $specimen_record->{dna_voucher_id_for_biobanking} = $s->{DNA_VOUCHER_ID_FOR_BIOBANKING};
          $specimen_record->{voucher_id}  = $s->{VOUCHER_ID};
          $specimen_record->{proxy_voucher_id}  = $s->{PROXY_VOUCHER_ID};
          $specimen_record->{voucher_link} = $s->{VOUCHER_LINK};
          $specimen_record->{proxy_voucher_link} = $s->{PROXY_VOUCHER_LINK};
          $specimen_record->{voucher_institution} = $s->{VOUCHER_INSTITUTION};
          $specimen_record->{preserver} = get_or_create_people($client,$s->{PRESERVED_BY},$s->{PRESERVER_AFFILIATION});
          $specimen_record->{collector} = get_or_create_people($client,$s->{COLLECTED_BY},$s->{COLLECTOR_AFFILIATION},$s->{COLLECTOR_ORCID_ID});
          $specimen_record->{identifier} = get_or_create_people($client,$s->{IDENTIFIED_BY},$s->{IDENTIFIER_AFFILIATION});
          $specimen_record->{coordinator} = get_or_create_people($client,$s->{SAMPLE_COORDINATOR},$s->{SAMPLE_COORDINATOR_AFFILIATION},$s->{SAMPLE_COORDINATOR_ORCID_ID});
          if ($s->{sampleDerivedFrom} =~ /\S/){
            $specimen_record->{biosampleAccession} = $s->{sampleDerivedFrom};
          }elsif ($s->{sampleSameAs} =~ /\S/){
            $specimen_record->{biosampleAccession} = $s->{sampleSameAs};
          }
          my $specimen_url = '';
          my $specimen_insert = encode_json $specimen_record;
          my $tid = $specimen_record->{tolid};
          my $specimenid = $specimen_record->{specimen_id};
          # CHECK if specimen exists in tracker. If so, we will PATCH. If not, POST.
          my $specimen_query = "$erga_status_url/specimen/?specimen_id=$specimenid";
          my $specimen_response = make_request($client,$specimen_query);
          if (! $specimen_response){
            print STDERR "Request timed out; Skipping ",$specimenid," and moving on...\n";
            next;
          } 
          if ($specimen_response->{count} > 0) {
            #PATCH
            print STDERR "Updating existing specimen record...\n" if $verbose;
            $specimen_url = $specimen_response->{results}->[0]->{url};
            $specimen_url =~s/10\.73\.4\.1/genomes.cnag.cat/;

            my $specimen_patch_response = make_patch($client,$specimen_url,$specimen_insert);
            if (! $specimen_patch_response){
              print STDERR "Request timed out; Skipping ",$specimen_url," and moving on...\n";
              next;
             } 
          }else{
            if ($s->{status} eq 'accepted' || $s->{status} eq 'pending' || $s->{status} eq 'rejected'){
              #POST
              print STDERR "\nInserting new specimen record...\n" if $verbose;
              my $specimen_insert_response = make_post($client,"$erga_status_url/specimen/", $specimen_insert);
              #if ($specimen_insert_response){$specimen_url = $specimen_insert_response->{results}->[0]->{url};}
              if (defined $specimen_insert_response and defined $specimen_insert_response->{url}){
                $specimen_url = $specimen_insert_response->{url};
              }
            }
          }
          my $specimen_response2 = make_request($client,$specimen_query);
          next if ! ($specimen_response2 or $specimen_response2->{count});
          $specimen_url = $specimen_response2->{results}->[0]->{url};

          my $record = {};
          $record->{copo_id} = $copo_id;
          $record->{biosampleAccession} = $sample_accession;
          $record->{species} = $species_id;
          $record->{barcode} = '';
          $record->{gal} = $s->{GAL};
          $record->{collector_sample_id} = $s->{COLLECTOR_SAMPLE_ID};
          $record->{copo_date} = $s->{time_updated};
          $record->{copo_status} = $s->{status};
          $record->{purpose_of_specimen} = $s->{PURPOSE_OF_SPECIMEN};
          $record->{tube_or_well_id} = $s->{TUBE_OR_WELL_ID};
          $record->{gal_sample_id} = $s->{GAL_SAMPLE_ID};
          $record->{specimen} = $specimen_url;
          $record->{sampleDerivedFrom} = $s->{sampleDerivedFrom};
          $record->{sampleSameAs} = $s->{sampleSameAs};
          #wrap it all up in JSON string
          my $insert = encode_json $record;
          # CHECK if sample exists in tracker. If so, we will PATCH. If not, POST.
          my $query = "$erga_status_url/sample/?copo_id=$copo_id ";
          my $response3 = make_request($client,$query);
          if ($response3 and $response3->{count} > 0) {
            #PATCH
            print STDERR "Updating existing sample record...\n" if $verbose;
            my $sample_url_r3 = $response3->{results}->[0]->{url};
            $sample_url_r3 =~s/10\.73\.4\.1/genomes.cnag.cat/;
            make_patch($client,$sample_url_r3, $insert);
          }else{
            if($s->{status} eq 'accepted' || $s->{status} eq 'pending' || $s->{status} eq 'bge_pending' || $s->{status} eq 'rejected'){
              print STDERR "Inserting new sample record...\n" if $verbose;
              make_post($client,"$erga_status_url/sample/", $insert);
            }
          }

          # Due to notification sent on save, genome team must exist before collection status
          my $genome_team_record = {};
          $genome_team_record->{sequencing_team} = $seqteam_url;
          $genome_team_record->{species} = $species_id;
          my $gt_insert = encode_json $genome_team_record;
          my $genome_team_query = "$erga_status_url/genome_team/?species=".$species_pk;
          my $gt_response = make_request($client,$genome_team_query);
          if ($gt_response->{count} > 0 ){
            if (!($gt_response->{results}->[0]->{sequencing_team}) || $gt_response->{results}->[0]->{sequencing_team} !~ /\w/){
              my $genometeam_url = $gt_response ->{results}->[0]->{url};
              $genometeam_url =~ s/10\.73\.4\.1/genomes.cnag.cat/;
              my $gt_insert_resp = make_patch($client,$genometeam_url, $gt_insert);
            }
          }else{
            my $post_gt_resp = make_post($client,"$erga_status_url/genome_team/", $gt_insert);
          }
          
          my $sample_collection_record = {};
          $sample_collection_record->{species} = $species_id;
          
          if ($s->{PURPOSE_OF_SPECIMEN} =~/REFERENCE_GENOME/){
            if($s->{status} eq 'accepted'){
              $bestcopostatus{$species_id}='Accepted';
              $sample_collection_record->{copo_status} = 'Accepted';
              $sample_collection_record->{genomic_sample_status} = 'Submitted';
            }
            if($s->{status} eq 'pending' && $bestcopostatus{$species_id} ne 'Accepted'){
              $bestcopostatus{$species_id}='Pending';
              $sample_collection_record->{copo_status} = 'Pending';
              $sample_collection_record->{genomic_sample_status} = 'Pending';
            }
            if($s->{status} eq 'rejected' && $bestcopostatus{$species_id} ne 'Accepted' && $bestcopostatus{$species_id} ne 'Pending'){
              $bestcopostatus{$species_id}='Rejected';
              $sample_collection_record->{copo_status} = 'Rejected';
            }
          }
          if ($s->{PURPOSE_OF_SPECIMEN} =~/RNA_SEQUENCING/){
              if($s->{status} eq 'accepted'){
              $bestcopostatusrna{$species_id}='Accepted';
              $sample_collection_record->{rna_sample_status} = 'Submitted';
            }
            if($s->{status} eq 'pending' && $bestcopostatusrna{$species_id} ne 'Accepted'){
              $bestcopostatusrna{$species_id}='Pending';
              $sample_collection_record->{rna_sample_status} = 'Pending';
            }
            if($s->{status} eq 'rejected' && $bestcopostatusrna{$species_id} ne 'Accepted' && $bestcopostatusrna{$species_id} ne 'Pending'){
              $bestcopostatusrna{$species_id}='Rejected';
              $sample_collection_record->{rna_sample_status} = 'Rejected';
            }
          }

          my $status_insert = encode_json $sample_collection_record;
          my $sample_collection_query = "$erga_status_url/sample_collection/?species=".$species_pk;
          my $response4 = make_request($client,$sample_collection_query);
          if ($response4 and $response4->{count} > 0) {
            print STDERR "Updating sample collection record...\n" if $verbose;
            my $collection_url = $response4 ->{results}->[0]->{url};
            $collection_url =~ s/10\.73\.4\.1/genomes.cnag.cat/;
            make_patch($client,$collection_url, $status_insert);
          }else{
            make_post($client,"$erga_status_url/sample_collection/", $status_insert);
          }
        }
      }
    }
    print STDERR "-------------\n\n" if $verbose;
  }
  return 1;
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
    }elsif ($response =~ /html/){
      print STDERR "$response\n";
      return 0;
    }else{
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
    }elsif ($response =~ /html/){
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
    }elsif ($response =~ /html/){
      print STDERR "$response\n";
      return 0;
    }elsif ($response =~ /Error/){
      print STDERR "$response\n";
      return 0;
    }else{
      return decode_json $response;
    }
}
sub get_or_create_affiliation{
    my $restclient = shift;
    my $affil_in = shift;
    my $affiliation = clean_text($affil_in);
    return 0 if not length($affiliation);
    my $url  = "$erga_status_url/affiliation/?affiliation=$affiliation";
    print STDERR "$url\n" if $verbose;
    my $getresp = make_request($restclient,$url);
    my $affiliation_url = '';
    if ($getresp and ($getresp->{count} > 0)) {
        print STDERR "Getting affiliation record...\n" if $verbose;
        $affiliation_url = $getresp ->{results}->[0]->{url};
    }else{
        my $affiliation_record = {};
        $affiliation_record->{affiliation} = $affiliation if $affiliation;
        my $affiliation_insert = encode_json $affiliation_record;
        my $postresp = "";
        $postresp = make_post($restclient,"$erga_status_url/affiliation/", $affiliation_insert);
        #print STDERR Data::Dumper->Dump([$postresp]),"\n";
        if (defined $postresp and defined $postresp->{url}) {
            $affiliation_url = $postresp->{url};
        }
    }
    return $affiliation_url;
}
sub get_or_create_people{
    my $restclient = shift;
    my $namestring = shift;
    my $affiliationstring = shift;
    my $orcidstring = '';
    $orcidstring = shift if @ARGV >3;
    my @orcids = ();
    my @names = ();
    my @affiliations = ();
    if ($namestring =~ /\|/){
      @names = split(/\|/,$namestring);
    }else{
      @names = split('\x{1c0}',$namestring);
    }
    if ($affiliationstring =~ /\|/){
      @affiliations = split(/\|/,$affiliationstring);
    }else{
      @affiliations = split('\x{1c0}',$affiliationstring);
    }
    if ($orcidstring =~ /\|/){
      @orcids = split(/\|/,$orcidstring);
    }else{
      @orcids = split('\x{1c0}',$orcidstring);
    }
    my $num_affs = scalar @affiliations;
    my $num_orcids = scalar @orcids;
    my $people = [];
    for(my $i = 0; $i < @names; $i++){
        $names[$i]=~s/^\s+//;
        $names[$i]=~s/\s+$//;
        my $this_affiliation = $affiliations[0];
        if ($num_affs >1){
          $this_affiliation = $affiliations[$i];
        }
        $this_affiliation=~s/^\s+//;
        $this_affiliation=~s/\s+$//;
        my $this_orcid = '';
        if (scalar @orcids){
          $this_orcid = $orcids[0];
          $this_orcid=~s/^\s+//;
          $this_orcid=~s/\s+$//;
        }
        my $p_url = get_or_create_person($restclient,clean_text($names[$i]),$this_affiliation,$orcids[0]);
        if ($num_orcids >1){
          $this_orcid = $orcids[$i];
          $this_orcid=~s/^\s+//;
          $this_orcid=~s/\s+$//;
          $p_url = get_or_create_person($restclient,clean_text($names[$i]),$this_affiliation,$orcids[$i]);
        }elsif($i>0){
          $this_orcid = 0;
          $p_url = get_or_create_person($restclient,clean_text($names[$i]),$this_affiliation);
        }
        print STDERR "PERSON: $p_url\n" if $verbose;
        push @$people,$p_url;
    }
    return $people;
}

sub get_or_create_person{
    my $restclient = shift;
    my $name = shift;
    my $affiliation = shift;
    #print STDERR "Affiliation in get_or_create_person:$affiliation\n";
    my $orcid = 0;
    $orcid = shift if @ARGV >3;
    my $person_url = '';
    my $aff_url = get_or_create_affiliation($restclient,$affiliation);
    my $url = "$erga_status_url/person/?name=$name";
    my $getresp = make_request($restclient,$url);
    my $sameperson = 0;
    if ($getresp and $getresp->{count} > 0) {
        print STDERR "$name exists; getting personal record...\n" if $verbose;
        foreach my $n (@{$getresp->{results}}){
            if ($orcid and $n->{orcid} eq $orcid){
              $sameperson = 1;
              $person_url = $n->{url};
            }else{
              foreach my $a (@{$n->{affiliation}}){
                if ($aff_url eq $a){
                  $sameperson = 1;
                  $person_url = $n->{url};
                }
              }

            }
        }
    }
    if(!$sameperson){
        print STDERR "$name not found; creating new person...\n" if $verbose;
        my $person_record = {};
        $person_record->{name} = $name;
        $person_record->{affiliation} = [$aff_url] if $aff_url;
        $person_record->{orcid} = $orcid if $orcid;
        my $person_insert = encode_json $person_record;
        my $postresp = undef;
        $postresp = make_post($restclient,"$erga_status_url/person/", $person_insert);
        if (defined $postresp and defined $postresp->{url}) {
            $person_url = $postresp->{url};
        }
    }
    return $person_url;
}

sub clean_text{
    my $input = shift;
    return $input;
    #my $decomposed = NFKD($input);
    #$decomposed =~ s/\p{NonspacingMark}//g;
    #$decomposed =~ s/Đ/D/g;
    #return unidecode($decomposed);
    #
    #return $decomposed;
}