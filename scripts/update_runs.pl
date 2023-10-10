#!/usr/bin/env perl
use lib "/home/groups/assembly/talioto/myperlmods/"; #change this to point to your PERL5LIB module directory or set the $PERL5LIB environment variable
#use lib '/home/groups/assembly/talioto/erga_scripts';
use REST::Client;
use MIME::Base64;
use JSON::PP;
#use Data::Dumper;
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

##### Sequencing Table Model
    # species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    # genomic_seq_status = models.CharField(max_length=20, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    # hic_seq_status = models.CharField(max_length=20, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    # rna_seq_status = models.CharField(max_length=20, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    # note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)
    # rnaseq_numlibs_target = models.IntegerField(null=True, blank=True, default=3, verbose_name="RNAseq libs target")
    # recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, to_field='name', default='HiFi25', verbose_name="Recipe", null=True)

##### Reads Table Model
    # project = models.ForeignKey(Sequencing, on_delete=models.CASCADE, verbose_name="Sequencing project")
    # ont_yield = models.BigIntegerField(null=True, blank=True, verbose_name="ONT yield")
    # hifi_yield = models.BigIntegerField(null=True, blank=True, verbose_name="HiFi yield")
    # hic_yield = models.BigIntegerField(null=True, blank=True, verbose_name="Hi-C yield")
    # short_yield = models.BigIntegerField(null=True, blank=True, verbose_name="Short read yield")
    # rnaseq_numlibs = models.IntegerField(null=True, blank=True, verbose_name="RNAseq libs")
    # ont_ena = models.CharField(max_length=12, null=True, blank=True, verbose_name="ONT Accession")
    # hifi_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="HiFi Accession")
    # hic_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="Hi-C Accession")
    # short_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="Short read Accession")
    # rnaseq_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="RNAseq Accession")
##### Run Table Model
    # project = models.ForeignKey(Sequencing, on_delete=models.CASCADE, verbose_name="Sequencing project")
    # read_type = models.CharField(max_length=15, help_text='Read type', choices=READ_TYPES, default=READ_TYPES[0][0])
    # seq_yield = models.BigIntegerField(null=True, blank=True, verbose_name="yield")
    # md5sum = models.CharField(max_length=32, help_text='Read 1 md5sum')

#### EXAMPLE TABLES ####

########################


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

  sequencing_runs_update.tsv has the following tab-delimited columns (this format is used by the ENA run submission script):
    center  scientific_name tolid   common_names    biosample_accession     sample_tube_or_well_id  sample_coordinator      recipe aim      locus_tag       alt_assembly    alt_annotation  instrument      library_selection       library_strategy        exp_attrlib_attr        yield   forward_file_name       forward_file_md5        reverse_file_name       reverse_file_md5        native_file_name        native_file_md5
  
    - For the ERGA-Stream update only the following fields are required to be filled:
        scientific_name or tolid_prefix
        read_type
        yield
        sample_tube_or_well_id (this needs to correspond to the tube_or_well_id submitted to COPO)
        forward_file_name
        all other filenames and md5sums are optional (but recommended)
  
  Fields not used by update_runs.pl but useful for submission of experiments and runs to the ENA:
    experiment_attributes run_attributes nominal_length nominal_sdev library_construction_protocol

  read_type choices: 'ONT', 'HiFi', 'Illumina', 'HiC', 'RNA'
  recipe choices: 
    'ONT60','HIFI25'
  instrument_model choices: 
    'Illumina NovaSeq 6000', 'PromethION', 'GridION', https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html#permitted-values-for-instrument
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
  print join("\t",@fields),"\n";
  for (my $i = 0;$i<@$sequpdate; $i++){
    #print STDERR "here1\n";
    my $tolid_prefix=$sequpdate->[$i]->{'tolid'};
    $tolid_prefix =~ s/\d+$//;
    my $scientific_name=$sequpdate->[$i]->{'scientific_name'};
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
    #my $status = $sequpdate->[$i]->{status};
    #print STDERR "yield: $yield\n";
    # if ($status !~/\S/){
    next if not $yield > 0;
    next if $yield eq '';
    # }
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

    if ($response2->{count} == 1) { #proceed if there is one and only one project
      $sequpdate->[$i]->{project}=$project_id;
      if ($sequpdate->[$i]->{'yield'} =~/\S/){

        # my $squery = "$erga_status_url/sample/?tube_or_well_id=".$sequpdate->[$i]->{'sample_tube_or_well_id'};
        # #print "$squery\n";
        # $client->GET($squery);
        # #print STDERR $client->responseContent(),"\n";
        # my $sample_response = decode_json $client->responseContent();
        # my $biosample = '';
        # my $sample_url = '';
        # my  $tolid = '';
        # if ($sample_response->{count} > 0) {
        #   $biosample = $sample_response->{results}->[0]->{biosampleAccession};
        #   $sample_url = $sample_response->{results}->[0]->{url};
        #   #print STDERR "BioSample Accession: $biosample\n";
        #   $sequpdate->[$i]->{'biosample_accession'} = $biosample;
        #   $sequpdate->[$i]->{'common_names'} = '';
        #   $sequpdate->[$i]->{'tolid'} = '';
        #   my $specimenquery = $sample_response->{results}->[0]->{'specimen'} ;
           
        #   #print "$specimenquery\n";
        #   $client->GET($specimenquery);
        #   #print STDERR $client->responseContent(),"\n";
        #   my $specimen_response = decode_json $client->responseContent();
        #   $tolid = $sample_response->{results}->[0]->{'tolid'};
        #   $sequpdate->[$i]->{'tolid'} = $tolid;
        # } else {die "Sample corresponding to ".$sequpdate->[$i]->{'sample_tube_or_well_id'}. " not found.\n";}
        my $sample_url = '';
        my $squery = "$erga_status_url/sample/?tube_or_well_id=".$sequpdate->[$i]->{'sample_tube_or_well_id'};
        $client->GET($squery);
        my $response_sample = decode_json $client->responseContent();
        #print STDERR $client->responseContent(),"\n\n";
        if ($response_sample->{count} > 0) {
          $sequpdate->[$i]->{'biosample_accession'} = $response_sample->{results}->[0]->{biosampleAccession};
          $sample_url = $response_sample->{results}->[0]->{url};
          $client->GET($response_sample->{results}->[0]->{specimen});
          #print STDERR $client->responseContent(),"\n\n";
          my $response_specimen = decode_json $client->responseContent();
          #print STDERR "tolid: ",$response_specimen->{tolid},"\n\n";
          $sequpdate->[$i]->{'tolid'} = $response_specimen->{tolid};
          
        }else{print STDERR "No sample found for $scientific_name with tube_or_well_id:",$sequpdate->[$i]->{'sample_tube_or_well_id'},"\n" and next;}

        $client->GET("$erga_status_url/reads/?project=". $project_id);
        my $readsresp = decode_json $client->responseContent();
        my $reads_url = $readsresp->{results}->[0]->{url};
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
        $read_insert_data{sample}=$sample_url;
        my $readinsert = encode_json \%read_insert_data;
        
        $client->GET("$erga_status_url/run/?sample_tube_or_well_id=". $sequpdate->[$i]->{'sample_tube_or_well_id'} ."&read_type=".$read_type ."&forward_filename=".$sequpdate->[$i]->{'forward_file_name'});
        my $response_reads = decode_json $client->responseContent();
        if ($response_reads->{count} > 0) {
          #PATCH
          print STDERR "Updating existing run record: \n",
          my $run_url = $response_reads->{results}->[0]->{url};
          $client->PATCH($run_url, $readinsert);
          #print STDERR $client->responseContent(),"\n";
        }else{
          #POST
          print STDERR "Inserting new run data... \n";
          $client->POST("$erga_status_url/run/", $readinsert);
          #print STDERR $client->responseContent(),"\n";
        }
        #print back table
        $sequpdate->[$i]->{'library_selection'} = 'RANDOM';

        foreach my $f (@fields){
          print exists($sequpdate->[$i]->{$f})?$sequpdate->[$i]->{$f}:"-";
          print "\t";
        }
        print "\n";
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
