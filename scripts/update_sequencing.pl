#!/usr/bin/env perl
use lib "/home/groups/assembly/talioto/myperlmods/"; #change this to point to your PERL5LIB module directory or set the $PERL5LIB environment variable
#use lib '/home/groups/assembly/talioto/erga_scripts';
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Data::Dumper;
use Getopt::Long;

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

  sequencing_update.tsv has the following columns:
  tolid_prefix  scientific_name genomic_seq_status  hic_seq_status  rna_seq_status  note  recipe  ont_yield hifi_yield  hic_yield short_yield rnaseq_pe

  either tolid_prefix OR scientific_name can be given
  recipe choices: 'ONT60','HIFI25'
  status choices: 'Waiting','Received','Extracted','Sequencing','TopUp','External','Done','Submitted','Issue'
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
print STDERR "Parsed data files... ready to update ERGA-Stream.\n";
my $client = REST::Client->new();
$client->addHeader('Content-Type', 'application/json');
$client->addHeader('charset', 'UTF-8');
$client->addHeader('Accept', 'application/json');
$client->addHeader('Authorization' => 'Basic '.encode_base64($config{'username'}.":".$config{'password'}));
update($seq_data,$erga_status_url);

sub update{
  my $sequpdate= shift;
  print STDERR Data::Dumper->Dump([$sequpdate]);
  my $erga_status_url = shift;
  for (my $i = 0;$i<@$sequpdate; $i++){
    my $tolid_prefix=$sequpdate->[$i]->{'tolid_prefix'};
    my $scientific_name=$sequpdate->[$i]->{'scientific_name'};
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
      print STDERR $client->responseContent(),"\n";
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
    print STDERR "Updating $project_url\n";
    my $project_id = $1;

    if ($response2->{count} == 1) { #proceed if there is one and only one project
      $sequpdate->[$i]->{project}=$project_id;
      my $genomic_seq_status=$sequpdate->[$i]->{genomic_seq_status};
      if (($genomic_seq_status =~/\S/) && ! exists $SEQUENCING_STATUS_CHOICES{$genomic_seq_status}){
        die "Status must be one of: ".join(", ",sort keys %SEQUENCING_STATUS_CHOICES)."\n";
      }
      my $hic_seq_status=$sequpdate->[$i]->{hic_seq_status};
      if (($hic_seq_status =~/\S/) && ! exists $SEQUENCING_STATUS_CHOICES{$hic_seq_status}){
        die "Status must be one of: ".join(", ",sort keys %SEQUENCING_STATUS_CHOICES)."\n";
      }
      my $rna_seq_status=$sequpdate->[$i]->{rna_seq_status};
      if (($rna_seq_status =~/\S/) && ! exists $SEQUENCING_STATUS_CHOICES{$rna_seq_status}){
        die "Status must be one of: ".join(", ",sort keys %SEQUENCING_STATUS_CHOICES)."\n";
      }
      my $note=$sequpdate->[$i]->{note};
      my $recipe=$sequpdate->[$i]->{recipe};
      my $ont_yield = $sequpdate->[$i]->{ont_yield};
      my $hifi_yield = $sequpdate->[$i]->{hifi_yield};
      my $hic_yield = $sequpdate->[$i]->{hic_yield};
      my $short_yield = $sequpdate->[$i]->{short_yield};
      my $rnaseq_pe = $sequpdate->[$i]->{rnaseq_pe};
      $client->GET("$erga_status_url/recipe/?name=". $recipe);
      my $recipe_response = decode_json $client->responseContent();
      my $recipe_url = $recipe_response->{results}->[0]->{url};

      my %seq_insert_data = ();
      $seq_insert_data{species}=$species_url;
      $seq_insert_data{genomic_seq_status}=$genomic_seq_status if $genomic_seq_status =~/\S/;
      $seq_insert_data{hic_seq_status}=$hic_seq_status if $hic_seq_status =~/\S/;
      $seq_insert_data{rna_seq_status}=$rna_seq_status if $rna_seq_status =~/\S/;
      $seq_insert_data{note}=$note if $note =~/\S/;
      $seq_insert_data{recipe}=$recipe if $recipe =~/\S/;;;
      my $seqinsert = encode_json \%seq_insert_data;
      
      my %read_insert_data = ();
      $read_insert_data{project}=$project_url;
      $read_insert_data{ont_yield}=$ont_yield if $ont_yield > 0;
      $read_insert_data{hifi_yield}=$hifi_yield if $hifi_yield > 0;
      $read_insert_data{hic_yield}=$hic_yield if $hic_yield > 0;
      $read_insert_data{short_yield}=$short_yield if $short_yield > 0;
      $read_insert_data{rnaseq_pe}=$rnaseq_pe if $rnaseq_pe > 0;
      my $readinsert = encode_json \%read_insert_data;
      
      print STDERR "Inserting sequencing update... \n";
      $client->PATCH($project_url, $seqinsert);
      print STDERR $client->responseContent(),"\n";
    
      $client->GET("$erga_status_url/reads/?project=". $project_id);
      #print STDERR $client->responseContent(),"\n";
      my $response_reads = decode_json $client->responseContent();
      if ($response_reads->{count} > 0) {
        #PATCH
        print STDERR "Updating existing reads record: \n",
        my $reads_url = $response_reads->{results}->[0]->{url};
        $client->PATCH($reads_url, $readinsert);
        print STDERR $client->responseContent(),"\n";
      }else{
        #POST
        print STDERR "Inserting new read data... \n";
        $client->POST("$erga_status_url/reads/", $readinsert);
        print STDERR $client->responseContent(),"\n";
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
  my @h = split /[,\t]/,$head;
  my $count=0;
  while (my $record = <TAB>) {
    chomp $record;
    my @r = split /[,\t]/,$record;

    for (my $i=0;$i<@h; $i++) {
      $arrayref->[$count]->{$h[$i]}=($r[$i]);
    }
    $count++;
  }
  close TAB;
  return $count?$arrayref:0;
}
