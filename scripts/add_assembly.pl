#!/usr/bin/env perl
use lib '/home/groups/assembly/talioto/erga_scripts';
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Data::Dumper;
use Getopt::Long;
my $conf = ".ergastream.cnf";
my $erga_status_url="https://genomes.cnag.cat/erga-stream/api";
my $printhelp = 0;
my $assembly_data;
my $assembly_tsv_file = 0;
my $verbose = 0;
GetOptions(
	   'c|config:s' => \$conf,
     'file|f:s' => \$assembly_tsv_file,
     'v' => \$verbose,
     'h|help' => \$printhelp
	  );
my $useage = <<'END_HELP';
usage: $0 -c <ergastream.cnf> -f assemblies.tsv
 
  The ergastream.cnf file has the format:
  URL:https://genomes.cnag.cat/erga-stream/api
  username:<username>
  password:<password>

  If using the development server or the URL changes at any time you can replace the url
  The username and passwords are the ones assigned to your team. If you'd like to use one attached to an email, 
  let Tyler know and he will grant your registered user the same priveleges.

  EXAMPLE assemblies.tsv (BUSCO string should be quoted or commas replaced with semicolons):
  tolid_prefix,description,pipeline version,type,span,contig_n50,scaffold_n50,chromosome_level,percent_placed,busco,busco_db,busco_version,qv
  odPhaVent,ratatosk.nextdenovo.hypo1.purged,CLAWS 2.1,Primary,207000000,2400000,6900000,FALSE,0,C:80.5%[S:78.4%;D:2.1%];F:8.5%;M:11.0%;n:954,metazoa_odb10,4.0.6,32.3
  ilHelHell,nextdenovo.assembly.hypo1.purged.curated,CLAWS 2.0,Primary,547306268,23624374,23624374,TRUE,100,C:98.0%[S:97.7%;D:0.3%];F:0.7%;M:1.3%;n:1013,arthropoda_odb10,4.0.6,46.6

  ASSEMBLY_TYPE_CHOICES = (
    ('Primary', 'Pseudohaploid Primary'),
    ('Alternate', 'Pseudohaploid Alternate'),
    ('Hap1', 'Phased Haplotype 1'),
    ('Hap2', 'Phased Haplotype 2'),
    ('Maternal', 'Trio-phased Maternal'),
    ('Paternal', 'Trio-phased Paternal'),
    ('MT', 'Mitogenome'),
    ('Chloroplast', 'Chloroplast'),
    ('Endosymbiont', 'Endosymbiont')
  )
END_HELP

if ($printhelp){
  print $usage;
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
die "please provide username in conf file" if (!exists $config{'username'});
die "please provide password in conf file" if (!exists $config{'password'});
my $client = REST::Client->new();
$client->addHeader('Content-Type', 'application/json');
$client->addHeader('charset', 'UTF-8');
$client->addHeader('Accept', 'application/json');
$client->addHeader('Authorization' => 'Basic '.encode_base64($config{'username'}.":".$config{'password'}));

#### EXAMPLE TABLES ####
#assemblies.tsv
#tolid_prefix,description,pipeline,type,span,contig_n50,scaffold_n50,chromosome_level,percent_placed,busco,busco_db,busco_version,qv

die "No assembly data!\n" unless $assembly_data=(loadTbl($assembly_tsv_file,$assembly_data));
print STDERR "Parsed data files... ready to add to ERGA-Status.\n";
print STDERR "Adding assembly data...\n"; #print STDERR Data::Dumper->Dump($assembly_data),"\n" and exit;
add_assembly($assembly_data);

sub add_assembly{
  my $assemblies = shift;
  for (my $i = 0;$i<@$assemblies; $i++){
    my $tolid_prefix=$assemblies->[$i]->{'tolid_prefix'};
    print STDERR "$tolid_prefix ",$assemblies->[$i]->{description},"\n";
    my $qv_rounded = sprintf("%.2f",$assemblies->[$i]->{qv});
    print STDERR $assemblies->[$i]->{qv},"\n";
    $assemblies->[$i]->{qv} = $qv_rounded ;
    my $pp_rounded = sprintf("%.1f",$assemblies->[$i]->{pct_placed});
    $assemblies->[$i]->{percent_placed} = $pp_rounded;

    #Retrieve species from target species table
    print STDERR "$erga_status_url/species/?tolid_prefix=". $tolid_prefix."\n";
    $client->GET("$erga_status_url/species/?tolid_prefix=". $tolid_prefix);
    my $response1 = decode_json $client->responseContent();
    my $species_url = $response1->{results}->[0]->{url};
    $species_url =~/(\d+)\/$/;
    my $species_id = $1;

    #Retrieve project based on species_id
    $client->GET("$erga_status_url/assembly_project/?species=". $species_id);
    my $response2 = decode_json $client->responseContent();
    my $project_url = $response2->{results}->[0]->{url};
    $project_url =~/(\d+)\/$/;
    #print STDERR "$project_url\n";
    my $project_id = $1;
    if ($response2->{count} == 1) { #proceed if there is one and only one project
      $assemblies->[$i]->{project}=$project_id;
      my $d=$assemblies->[$i]->{description};
      my $assemblypipeline=$assemblies->[$i]->{pipeline};
      my $type=$assemblies->[$i]->{type};
      my $span=$assemblies->[$i]->{span};
      my $chr_level=$assemblies->[$i]->{chr_level};
      my $cn50=$assemblies->[$i]->{contig_n50};
      my $sn50=$assemblies->[$i]->{scaffold_n50};
      my $busco=$assemblies->[$i]->{busco};
      my $busco_db=$assemblies->[$i]->{busco_db};
      my $busco_version=$assemblies->[$i]->{busco_version};
      my $report=$assemblies->[$i]->{report};

      #Get the pipeline. If it doesn't exist, add it via the admin interface and come back and do this again.
      if (length($assemblypipeline)){
        die "pipeline must be in format <name> <version>" if $assemblypipeline !~/\S\s\S/;
        my ($pipeline_name,$pipeline_version)= split /\s/,$assemblypipeline;
        my $pipeline_response = make_request($client,"$erga_status_url/assembly_pipeline/?name=$pipeline_name&version=$pipeline_version");
        my $pipeline_url = '';
        if ($pipeline_response->{count} > 0) {
          $pipeline_url = $pipeline_response->{results}->[0]->{url};
        }else{
          print STDERR "Pipeline $assemblypipline not found: please add it using the admin panel\n";
        }
      }
      

      #Get the busco_db. If it doesn't exist, add it.
      my $busco_db_response = make_request($client,"$erga_status_url/busco_db/?db=". $busco_db);
      my $busco_db_url = '';
      if ($busco_db_response->{count} > 0) {
        $busco_db_url = $busco_db_response->{results}->[0]->{url};
      }else{
        my $busco_entry;
        $busco_entry->{db}=$busco_db;
        my $post_resp = make_post($client,"$erga_status_url/busco_db/", encode_json($busco_entry));
      }
      #Get the BUSCO version. If it doesn't exist, add it.
      my $busco_version_response = make_request($client,"$erga_status_url/busco_version/?version=$busco_version");
      my $busco_version_url = $busco_version_response->{results}->[0]->{url};
      #Replace regular strings with REST URLs.
      $assemblies->[$i]->{project}=$project_url;
      $assemblies->[$i]->{busco_db}=$busco_db_url;
      $assemblies->[$i]->{busco_version}=$busco_version_url;
      $assemblies->[$i]->{pipeline}=pipeline_url;

      #wrap it all up in JSON string
      my $insert = encode_json $assemblies->[$i];
      #check to see if the assembly already exists. patch entry if it does.
      my $query = "$erga_status_url/assembly/?project=$project_id&description=$d&contig_n50=$cn50&scaffold_n50=$sn50&qv=$qv";
      my $response3 = make_request($client,$query);
      if ($response3->{count} > 0) {
        print STDERR "Possible duplicate: $d\n",encode_json($response3),"\nPatching...\n";
          my $found_assembly_url = $response3->{results}->[0]->{url};
          my $patch_response = make_patch($client,$found_assembly_url, $insert);
      }else{
        my $post_resp = make_post($client,"$erga_status_url/assembly/", $insert);
      }
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
sub make_request{
  my $client= shift;
  my $query = shift;
  print STDERR "$query\n" if $verbose;
  my $response = "";
    for (my $i=0; $i<10; $i++){
      $client->GET($query);
      $response = $client->responseContent();
      last if $response !~ /timeout/;
      sleep 1;
    }
    if ($response =~ /timeout/){
      return 0;
    }elsif ($response =~ /html/){
      print STDERR "$response\n";
      return 0;
    }else{
      print STDERR "$response\n" if $verbose;
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
      last if $response !~ /timeout/;
      sleep 1;
    }
    if ($response =~ /timeout/){
      return 0;
    }elsif ($response =~ /html/){
      print STDERR "$response\n";
      return 0;
    }else{
      print STDERR "$response\n" if $verbose;
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
      print STDERR "$response\n" if $verbose;
      return decode_json $response;
    }
}