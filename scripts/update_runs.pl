#!/usr/bin/env perl
use lib "/home/groups/assembly/talioto/myperlmods/"; #change this to point to your PERL5LIB module directory or set the $PERL5LIB environment variable
use lib '/home/groups/assembly/talioto/erga_scripts';
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Getopt::Long;
use strict;
use File::Basename qw( fileparse );

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
usage: update_sequencing.pl [-h] [-c <ergastream.cnf>] -f <sequencing_runs_update.tsv>
 
  The ergastream configuration file (default name: ".ergastream.cnf") has the format:
    URL https://genomes.cnag.cat/erga-stream/api
    username  <username>
    password  <password>

  If using the development server or the URL changes at any time, you can replace the URL.
  The username and passwords are the ones assigned to your team. If you'd like to use one attached to an email, 
  let Tyler know and he will grant your registered user the same priveleges.

  sequencing_runs_update.tsv has the following tab-delimited columns:
    center 
    scientific_name (* one or the other of scientific_name or tolid_prefix is required)
    tolid (* one or the other of scientific_name or tolid_prefix is required)
    common_names   
    biosample_accession 
    sample_tube_or_well_id *
    sample_coordinator 
    recipe aim
    locus_tag
    alt_assembly
    alt_annotation
    instrument *
    library_selection 
    library_strategy *
    exp_attrlib_attr
    yield *
    forward_file_name *
    forward_file_md5
    reverse_file_name
    reverse_file_md5
    native_file_name
    native_file_md5
  
    - For the ERGA-Stream update only the following fields are required to be filled:
        scientific_name or tolid_prefix
        sample_tube_or_well_id (this needs to correspond to the tube_or_well_id submitted to COPO)
        instrument
        library_strategy
        yield
        forward_file_name
        all other fields are optional (but recommended as they can be useful for submission of runs to the ENA)

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
my ($base,$path,$ext) = fileparse($sequencing_tsv_file,qw(\.tsv \.tab \.txt));
my $outfile = "$base.withBiosample.tsv";
open (OUT, ">$outfile");
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
  my @fields = qw(
        center 
        scientific_name 
        tolid 
        common_names 
        biosample_accession 
        sample_tube_or_well_id 
        sample_coordinator 
        recipe 
        aim 
        locus_tag 
        alt_assembly 
        alt_annotation 
        instrument 
        library_selection 
        library_strategy 
        exp_attr 
        lib_attr 
        yield 
        forward_file_name 
        forward_file_md5 
        reverse_file_name 
        reverse_file_md5 
        native_file_name 
        native_file_md5
        );
  print OUT join("\t",@fields),"\n"; #print header of returned output table, with retrieved biosample accession added.
  for (my $i = 0;$i<@$sequpdate; $i++){
    my $tolid_prefix=$sequpdate->[$i]->{'tolid'};
    $tolid_prefix =~ s/\d+$//;
    my $scientific_name=$sequpdate->[$i]->{'scientific_name'};
    print STDERR "$scientific_name\n";
    my $instrument=$sequpdate->[$i]->{'instrument'};
    my $library_strategy=$sequpdate->[$i]->{'library_strategy'};
    my $out_library_strategy = "WGS";
    my $read_type = '';
    if ($library_strategy =~ /RNA-?Seq/i){$read_type = "RNA";$library_strategy = "RNA-Seq";}
    if ($instrument =~ /^Illumina/i && $library_strategy =~  /WGS/i){$read_type = "Illumina";$library_strategy = "WGS";}
    if ($instrument =~ /(PacBio|Revio|Sequel)/i  && $library_strategy =~ /WGS/i){$read_type = "HiFi";$library_strategy = "WGS";}
    if ($instrument =~ /^Illumina/i && $library_strategy =~ /Hi-?C/i){$read_type = "HiC";$library_strategy = "Hi-C";}
    if ($instrument =~ /ION$/i && $library_strategy =~ /WGS/i){$read_type = "ONT";$library_strategy = "WGS";}
    my $yield=$sequpdate->[$i]->{'yield'};
    next if not $yield > 0;
    next if $yield eq '';
    print STDERR "yield: $yield\n";
    my $species_id = 0;
    my $species_url = 0;
    if ($tolid_prefix =~m/\w/){
      #Retrieve species from target species table
      $client->GET("$erga_status_url/species/?tolid_prefix=". $tolid_prefix);
          print STDERR $client->responseContent(),"\n\n";
      my $response1 = decode_json $client->responseContent();
      $species_url = $response1->{results}->[0]->{url};
      $species_url =~/(\d+)\/$/;
      $species_id = $1;
    }elsif($scientific_name =~m/\w/){
      #Retrieve species from target species table
      $client->GET("$erga_status_url/species/?scientific_name=". $scientific_name);
          print STDERR $client->responseContent(),"\n\n";
      my $response1 = decode_json $client->responseContent();
      $species_url = $response1->{results}->[0]->{url};
      $species_url =~/(\d+)\/$/;
      $species_id = $1;
    }else{
      die "please provide tolid or scientific_name\n";
    }

    #Retrieve project based on species_id
    $client->GET("$erga_status_url/sequencing/?species=". $species_id);
          print STDERR $client->responseContent(),"\n\n";
    my $response2 = decode_json $client->responseContent();
    my $project_url = $response2->{results}->[0]->{url};
    $project_url =~/(\d+)\/$/;
    my $project_id = $1;
    print STDERR "project id: $project_id\n";

    if ($response2->{count} == 1) { #proceed if there is one and only one project
      $sequpdate->[$i]->{project}=$project_id;
      my $tubestring = $sequpdate->[$i]->{'sample_tube_or_well_id'};
      my $first_tube = $tubestring;
      my $pool = 0;
      my @tubes = ();
      my $sample_url = '';
      if ($tubestring=~/[,;]/){
        $tubestring =~ s/\s//g;
        @tubes = split /[,;]/, $tubestring;
        $first_tube = $tubes[0];
        $pool = 1;
      }else{push @tubes, $tubestring;}
      if ($sequpdate->[$i]->{'yield'} =~/\S/){
        if ($tubestring =~ /\S/){
          my @biosample_accessions = ();
          foreach my $t (@tubes){
            ### try tube id first
            my $squery = "$erga_status_url/sample/?tube_or_well_id=".$t ;
            $client->GET($squery);
            print STDERR $client->responseContent(),"\n\n";
            my $response_sample = decode_json $client->responseContent();

            if ($response_sample->{count} > 0) {
              #$sequpdate->[$i]->{'sampleDerivedFrom'} = $response_sample->{results}->[0]->{sampleDerivedFrom};
              push @biosample_accessions, $response_sample->{results}->[0]->{biosampleAccession};
              # if ($pool){
              #   $sequpdate->[$i]->{'biosample_accession'} = $response_sample->{results}->[0]->{sampleDerivedFrom};
              # }
              $sample_url = $response_sample->{results}->[0]->{url};
              $client->GET($response_sample->{results}->[0]->{specimen});
              print STDERR $client->responseContent(),"\n\n";
              my $response_specimen = decode_json $client->responseContent();
              #print STDERR "tolid: ",$response_specimen->{tolid},"\n\n";
              $sequpdate->[$i]->{'tolid'} = $response_specimen->{tolid};
            }else{
              $squery = "$erga_status_url/sample/?gal_sample_id=".$t ;
              $client->GET($squery);
              my $response_sample_gal_sample_id = decode_json $client->responseContent();
              print STDERR $client->responseContent(),"\n\n";
              if ($response_sample_gal_sample_id->{count} > 0) {
                #$sequpdate->[$i]->{'sampleDerivedFrom'} = $response_sample->{results}->[0]->{sampleDerivedFrom};
                push @biosample_accessions, $response_sample_gal_sample_id->{results}->[0]->{biosampleAccession};
                # if ($pool){
                #   $sequpdate->[$i]->{'biosample_accession'} = $response_sample->{results}->[0]->{sampleDerivedFrom};
                # }
                $sample_url = $response_sample_gal_sample_id->{results}->[0]->{url};
                $client->GET($response_sample_gal_sample_id->{results}->[0]->{specimen});
                #print STDERR $client->responseContent(),"\n\n";
                my $response_specimen = decode_json $client->responseContent();
                #print STDERR "tolid: ",$response_specimen->{tolid},"\n\n";
                $sequpdate->[$i]->{'tolid'} = $response_specimen->{tolid};
              }else{
                print STDERR "No sample found for $scientific_name with tube_or_well_id or gal_sample_id:",$t,"\n";
              }
            }

          }
          $sequpdate->[$i]->{'biosample_accession'} = join(",",@biosample_accessions);
        }

        $client->GET("$erga_status_url/reads/?project=". $project_id);
        print STDERR "$erga_status_url/reads/?project=$project_id\n";
        print STDERR $client->responseContent();
        my $reads_url = '';
        my $readsresp = decode_json $client->responseContent();
        if ($readsresp->{count} == 0) {
          #reads record doesn't exist. Need to insert it.
          my %read_rec = ();
          $read_rec{'project'}=$project_url;
          $client->POST("$erga_status_url/reads/", encode_json \%read_rec);
          $client->GET("$erga_status_url/reads/?project=". $project_id);
          my $readsresp2 = decode_json $client->responseContent();
          $reads_url = $readsresp2->{results}->[0]->{url};
        }else{
          $reads_url = $readsresp->{results}->[0]->{url};
        }
        my %read_insert_data = ();
        $read_insert_data{project}=$project_url;
        $read_insert_data{tube_or_well_id}=$sequpdate->[$i]->{'sample_tube_or_well_id'};
        $read_insert_data{read_type}=$read_type;
        $read_insert_data{seq_yield}=$sequpdate->[$i]->{'yield'};
        $read_insert_data{forward_filename}=$sequpdate->[$i]->{'forward_file_name'};
        $read_insert_data{forward_md5sum}=$sequpdate->[$i]->{'forward_file_md5'};
        $read_insert_data{reverse_filename}=$sequpdate->[$i]->{'reverse_file_name'};
        $read_insert_data{reverse_md5sum}=$sequpdate->[$i]->{'reverse_file_md5'};
        $read_insert_data{native_filename}=$sequpdate->[$i]->{'native_file_name'};
        $read_insert_data{native_md5sum}=$sequpdate->[$i]->{'native_file_md5'};
        $read_insert_data{reads}=$reads_url;
        $read_insert_data{sample}=$sequpdate->[$i]->{'biosample_accession'}; #$sample_url;
        my $readinsert = encode_json \%read_insert_data;
        
        $client->GET("$erga_status_url/run/?read_type=".$read_type ."&forward_filename=".$sequpdate->[$i]->{'forward_file_name'});
        my $response_reads = decode_json $client->responseContent();
        if ($response_reads->{count} > 0) {
          #PATCH
          print STDERR "Updating existing run record: \n",
          my $run_url = $response_reads->{results}->[0]->{url};
          $client->PATCH($run_url, $readinsert);
          print STDERR "\n";
          print STDERR $client->responseContent(),"\n";
        }else{
          #POST
          print STDERR "Inserting new run data... \n";
          $client->POST("$erga_status_url/run/", $readinsert);
          print STDERR "$readinsert\n";
          print STDERR $client->responseContent(),"\n";
        }
        #print back table
        $sequpdate->[$i]->{'library_selection'} = 'RANDOM';
        foreach my $f (@fields){
          if (exists($sequpdate->[$i]->{$f}) && $sequpdate->[$i]->{$f} =~ /\S/){
            print OUT $sequpdate->[$i]->{$f};
          }else{
            print OUT '-';
          }
          #print (exists($sequpdate->[$i]->{$f}) && $sequpdate->[$i]->{$f} =~ /\S/)?$sequpdate->[$i]->{$f}:"-";
          print OUT "\t";
        }
        print OUT "\n";
      }
    } else {
      print STDERR "Couldn't find project. Please add project for $scientific_name $tolid_prefix via the admin interface. Skipping for now.\n"; 
    }
  }
  close OUT;
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
