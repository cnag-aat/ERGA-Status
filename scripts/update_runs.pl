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
usage: update_sequencing.pl [-h] [-c <ergastream.cnf>] -f <sequencing_update.tsv>
 
  The ergastream configuration file (default name: ".ergastream.cnf") has the format:
    URL https://genomes.cnag.cat/erga-stream/api
    username  <username>
    password  <password>

  If using the development server or the URL changes at any time, you can replace the URL.
  The username and passwords are the ones assigned to your team. If you'd like to use one attached to an email, 
  let Tyler know and he will grant your registered user the same priveleges.

  sequencing_update.tsv has the following tab-delimited columns:
    center scientific_name tolid_prefix recipe read_type status notes sample_tube_or_well_id instrument_model yield forward_file_name forward_file_md5 reverse_file_name reverse_file_md5 experiment_attributes run_attributes nominal_length nominal_sdev library_construction_protocol

  Two types of records are parsed from the tsv: status updates and sequencing runs. These can be in the same tsv or submitted via separate tsvs.
    - Status update records require the following fields:
        scientific_name or tolid_prefix
        recipe
        read_type
        status
        notes (optional)

    - Run records require the following fields:
        scientific_name or tolid_prefix
        read_type
        yield
        forward_file_name
        sample_tube_or_well_id (this should correspond to the tube_or_well_id submitted to COPO)
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
  for (my $i = 0;$i<@$sequpdate; $i++){
    my $tolid_prefix=$sequpdate->[$i]->{'tolid_prefix'};
    my $scientific_name=$sequpdate->[$i]->{'scientific_name'};
    my $read_type=$sequpdate->[$i]->{'read_type'};
    my $yield=$sequpdate->[$i]->{'yield'};
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
      my $status=$sequpdate->[$i]->{status};
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
        $seq_insert_data{note}=$note if $note =~/\S/;
        $seq_insert_data{recipe}=$recipe if $recipe =~/\S/;
        my $seqinsert = encode_json \%seq_insert_data;
        
        print STDERR "Updating $project_url\n";
        $client->PATCH($project_url, $seqinsert);
      }
      if ($sequpdate->[$i]->{'yield'} =~/\S/){
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
        my $readinsert = encode_json \%read_insert_data;
        
        $client->GET("$erga_status_url/run/?sample_tube_or_well_id=". $sequpdate->[$i]->{'sample_tube_or_well_id'} ."&read_type=".$read_type ."&forward_filename=".$sequpdate->[$i]->{'forward_file_name'});
        my $response_reads = decode_json $client->responseContent();
        if ($response_reads->{count} > 0) {
          #PATCH
          print STDERR "Updating existing run record: \n",
          my $run_url = $response_reads->{results}->[0]->{url};
          $client->PATCH($run_url, $readinsert);
          print STDERR $client->responseContent(),"\n";
        }else{
          #POST
          print STDERR "Inserting new run data... \n";
          $client->POST("$erga_status_url/run/", $readinsert);
          print STDERR $client->responseContent(),"\n";
        }
      }
    } else {
      print STDERR "Couldn't find project. Please add project for $tolid_prefix via the admin interface. Skipping for now.\n"; 
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
