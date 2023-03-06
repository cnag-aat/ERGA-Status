#!/usr/bin/env perl
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Data::Dumper;
use Getopt::Long;
my $conf = ".ergastream.cnf";
my $erga_status_url="https://genomes.cnag.cat/erga-stream/api";
my $printhelp = 0;
my $seq_data;
my $sequencing_tsv_file = 0;

# get status label from the db
my %SEQUENCING_STATUS_CHOICES = {
  'Waiting'=>1,
  'Received'=>1,
  'Extracted'=>1,
  'Sequencing'=>1,
  'TopUp'=>1,
  'External'=>1,
  'Submitted'=>1,
  'Done'=>1,
  'Issue'=>1
};


##### Sequencing Table Model
    # species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    # genomic_seq_status = models.CharField(max_length=20, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    # hic_seq_status = models.CharField(max_length=20, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    # rna_seq_status = models.CharField(max_length=20, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    # note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)
    # rnaseq_numlibs_target = models.IntegerField(null=True, blank=True, default=3, verbose_name="RNAseq libs target")
    # recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, to_field='name', default='HiFi25', verbose_name="Recipe", null=True)

#### EXAMPLE TABLES ####

########################

GetOptions(
	   'c|config:s' => \$conf,
     'f|file:s' => \$sequencing_tsv_file,
     'h|help' => \$printhelp
	  );
my $usage = <<'END_HELP';
usage: update_sequencing.pl [-c <ergastream.cnf>] [-h] -f <sequencing_update.tsv>
 
  The ergastream.cnf file has the format:
    URL:https://genomes.cnag.cat/erga-stream/api
    username:<username>
    password:<password>

  If using the development server or the URL changes at any time you can replace the url
  The username and passwords are the ones assigned to your team. If you'd like to use one attached to an email, 
  let Tyler know and he will grant your registered user the same priveleges.

END_HELP

if ($printhelp or !$sequencing_tsv_file){
  print $usage and exit;
}
open(CONF,"<$conf") or die "Configuration file $conf does not exist. Please create it in the current working directory or specify the path to it using the -c option.";
my %config = ();
while(my $l = <CONF>){
  chomp $l;
  print "$l\n";
  my ($k,$v)=split(/\s+/,$l);
  print "$v\n";
  $config{$k}=$v;
}
if(exists $config{'URL'}){
  $erga_status_url=$config{'URL'}
}

die "please provide username in conf file" if (! exists($config{'username'}));
die "please provide password in conf file" if (!exists($config{'password'}));
die "No seq data!\n" unless $seq_data=(loadTbl($sequencing_tsv_file,$seq_data));

my $client = REST::Client->new();
$client->addHeader('Content-Type', 'application/json');
$client->addHeader('charset', 'UTF-8');
$client->addHeader('Accept', 'application/json');
$client->addHeader('Authorization' => 'Basic '.encode_base64($config{'username'}.":".$config{'password'}));


print STDERR "Parsed data files... ready to add to ERGA-Status.\n";
print STDERR "Adding seq data...\n"; #print STDERR Data::Dumper->Dump($assembly_data),"\n" and exit;
#exit;
update($seq_data,$erga_status_url);

sub update{
  my $sequpdate= shift;
  my $erga_status_url = shift;
  for (my $i = 0;$i<@$sequpdate; $i++){
    my $tolid_prefix=$sequpdate->[$i]->{'tolid_prefix'};
    my $scientific_name=$sequpdate->[$i]->{'scientific_name'};
    my $species_id = 0;
    print STDERR "$tolid_prefix\n";
    if ($tolid_prefix =~m/\w/){
      #Retrieve species from target species table
      print STDERR  "$erga_status_url/species/?tolid_prefix=". $tolid_prefix."\n";
      $client->GET("$erga_status_url/species/?tolid_prefix=". $tolid_prefix);
      #print $client->responseContent() and exit;
      my $response1 = decode_json $client->responseContent();
      my $species_url = $response1->{results}->[0]->{url};
      $species_url =~/(\d+)\/$/;
      $species_id = $1;
    }elsif($scientific_name =~m/\w/){
      #Retrieve species from target species table
      $client->GET("$erga_status_url/species/?scientific_name=". $scientific_name);
      my $response1 = decode_json $client->responseContent();
      my $species_url = $response1->{results}->[0]->{url};
      $species_url =~/(\d+)\/$/;
      $species_id = $1;
    }else{die "please provide tolid or scientific_name\n"}

    #Retrieve project based on species_id
    $client->GET("$erga_status_url/sequencing/?species=". $species_id);
    my $response2 = decode_json $client->responseContent();
    #print STDERR $client->responseContent() and exit;
    my $project_url = $response2->{results}->[0]->{url};
    $project_url =~/(\d+)\/$/;
    print STDERR "$project_url\n";
    my $project_id = $1;
    exit;
    if ($response2->{count} == 1) { #proceed if there is one and only one project
      $sequpdate->[$i]->{project}=$project_id;
      my $genomic_seq_status=$sequpdate->[$i]->{genomic_seq_status};
      my $hic_seq_status=$sequpdate->[$i]->{hic_seq_status};
      my $rna_seq_status=$sequpdate->[$i]->{rna_seq_status};
      my $note=$sequpdate->[$i]->{note};
      my $rnaseq_numlibs_target=$sequpdate->[$i]->{rnaseq_numlibs_target};
      my $recipe=$sequpdate->[$i]->{recipe};

      #Get the busco_db. If it doesn't exist, add it via the admin interface and redo this. In future, we can do it here.
      $client->GET("$erga_status_url/busco_db/?db=". $busco_db);
      my $busco_db_response = decode_json $client->responseContent();
      my $busco_db_url = $busco_db_response->{results}->[0]->{url};

      #Get the BUSCO version. If it doesn't exist, add it via the admin interface and redo this. In future, we can do it here.
      $client->GET("$erga_status_url/busco_version/?species=". $busco_version);
      my $buso_version_response = decode_json $client->responseContent();
      my $busco_version_url = $busco_version_response->{results}->[0]->{url};

      #check to see if the assembly already exists. Give warning.
      my $query = "$erga_status_url/assembly/?project=$project_id&description=$d&contig_n50=$cn50&scaffold_n50=$sn50&qv=$qv";
      #print "$query\n";
      $client->GET($query);
      my $response3 = decode_json $client->responseContent();
      if ($response3->{count} > 0) {
        print STDERR "Possible duplicate: $d\n",encode_json($response3),"\nAdding anyway. You may want to manually remove this record.\n";
      }
      #Replace regular strings with REST URLs.
      $sequpdate->[$i]->{project}=$project_url;
      $sequpdate->[$i]->{busco_db}=$busco_db_url;
      $sequpdate->[$i]->{busco_version}=$busco_version_url;

      #wrap it all up in JSON string
      my $insert = encode_json $sequpdate->[$i];
      #print STDERR "$insert\n";
      $client->POST("$url/assembly/", $insert);
      print STDERR "Inserting... Response:",$client->responseContent(),"\n";
    } else {
      print STDERR "Couldn't find project. Please add project for $tolid_prefix via the admin interface. Skipping for now.\n"; #print STDERR "Project could not be found in the samples table. Please add sample first.\n",encode_json($response2),"\n";
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
  my @h = split "\t",$head;
  my $count=0;
  while (my $record = <TAB>) {
    chomp $record;
    my @r = split "\t",$record;

    for (my $i=0;$i<@h; $i++) {
      $arrayref->[$count]->{$h[$i]}=($r[$i]);
    }
    $count++;
  }
  close TAB;
  return $count?$arrayref:0;
}
