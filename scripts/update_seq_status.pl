#!/usr/bin/env perl
use lib "/home/groups/assembly/talioto/myperlmods/"; #change this to point to your PERL5LIB module directory or set the $PERL5LIB environment variable
use lib '/home/groups/assembly/talioto/erga_scripts';
use REST::Client;
use MIME::Base64;
use JSON::PP;
use Data::Dumper;
use Getopt::Long;
my $conf = ".ergastream.cnf";
my $erga_status_url="https://genomes.cnag.cat/erga-stream/api";
my $printhelp = 0;
my $verbose = 0;
#my $status_only = 0;
GetOptions(
	   	'c|config:s' => \$conf,
     	'h|help' => \$printhelp,
  		'v|verbose' => \$verbose,
		#'status' => \$status_only
	  );
my $useage = <<'END_HELP';
usage: $0 -c <ergastream.cnf>
 
The ergastream.cnf file has the format:
URL:https://genomes.cnag.cat/erga-stream/api
username:<username>
password:<password>

If using the development server or the URL changes at any time you can replace the url
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
$client->setTimeout(10);

my $enaclient = REST::Client->new();
$enaclient->addHeader('Content-Type', 'application/json');
$enaclient->addHeader('charset', 'UTF-8');
$enaclient->addHeader('Accept', 'application/json');
my $ena_url = "https://www.ebi.ac.uk/ena/portal/api/search";
my $usage = <<'END_HELP';
usage: $0

END_HELP

# my $squery = "$erga_status_url/sample/";
# print "$squery\n";
# $client->GET($squery);
# #print STDERR $client->responseContent(),"\n";
# my $sample_response = decode_json $client->responseContent();
# my $biosample = '';
# my $sample_url = '';
# if ($sample_response->{count} > 0) {
# 	my $sample_accession = '';
# 	foreach $mysample (@{$sample_response->{results}}){
# 		my $sample_accession = $mysample->{biosampleAccession};
# 		my $sampleDerivedFrom_accession = $mysample->{sampleDerivedFrom};
# 		my $sampleSameAs_accession = $mysample->{sampleSameAs};
# 		next if $sample_accession !~/\S/;
# 		update($sample_accession);
# 		if ($sampleDerivedFrom_accession =~/\S/){update($sampleDerivedFrom_accession);}
# 		if ($sampleSameAs_accession =~/\S/){update($sampleSameAs_accession);}
# 	}
# }
	
my %projects = ();

#my $sample_accession = shift;
#library_strategy Hi-C, WGS, RNA-Seq, OTHER
#Instrument_platform OXFORD_NANOPORE PACBIO_SMRT ILLUMINA
#y $sample_accession = shift @ARGV;

#### Query the ENA for the experiment
#my $ena_query = "$ena_url/?result=read_experiment&query=study_accession%2Cexperiment_accession%2Caccession%2Cinstrument_platform%2Ccenter_name%2Ctax_id%2Ctissue_type%2Cstudy_title%2Csequencing_method%2Csample_title%2Cscientific_name%2Clibrary_strategy%2Cbase_count&format=jsonsample_accession%3D%22$sample_accession%22&fields=";
# curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_experiment&query=sample_accession%3D%22SAMEA12832259%22&fields=accession%2Ccenter_name%2Ctax_id%2Ctissue_type%2Cstudy_title%2Cstudy_accession%2Csequencing_method%2Csample_title%2Cscientific_name%2Cproject_name%2Clibrary_strategy&format=json "https://www.ebi.ac.uk/ena/portal/api/search"
my $ena_query = "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJEB61747&result=read_run&fields=run_accession,experiment_accession,study_accession,sample_accession,scientific_name,tax_id,base_count,read_count,instrument_platform,library_strategy,center_name,submitted_md5,library_construction_protocol,last_updated&format=json";

$enaclient->GET($ena_query);
print STDERR "$ena_query\n";
#print STDERR "ENA Response:", $enaclient->responseContent(),"\n";
my $ena_json = $enaclient->responseContent();
if ($ena_json){
	my $ena_response = decode_json $ena_json;
	#print Data::Dumper->Dump([$ena_response]);
	my $number_found = scalar @$ena_response;
	print STDERR "$number_found runs found.\n";
	if ($number_found){
		foreach my $r (@$ena_response){
			#next if $r->{tax_id} ne '2053936'; #test ilGraIsab
			next if $r->{base_count} < 1;
			my $proj_url = '';
			my $species_query = "$erga_status_url/species/?taxon_id=".$r->{tax_id};
			#print STDERR $species_query,"\n";
			# my $species_response = '';
			# for (my $i=0; $i<10; $i++){
			# 	$client->GET($species_query);
			# 	$species_response = $client->responseContent();
			# 	last if $species_response !~ /timeout/;
			# }
			# if ($species_response =~ /timeout/){
			# 	"Request timed out; Skipping and going to next run...\n";
			# 	next;
			# }
			my $species_data = make_request($client,$species_query); #decode_json $species_response;
			my $species_url = $species_data->{results}->[0]->{url};
			#print STDERR $species_url,"\n";
			$species_url =~/(\d+)\/$/;
			my $species_id = $1;
			my $sequencing_query = "$erga_status_url/sequencing/?species=".$species_id;
			#print STDERR $sequencing_query,"\n";
			# my $sequencing_response = "";
			# for (my $i=0; $i<10; $i++){
			# 	$client->GET($sequencing_query);
			# 	$sequencing_response = $client->responseContent();
			# 	last if $sequencing_response !~ /timeout/;
			# 	sleep 1;
			# }
			# if ($sequencing_response =~ /timeout/){
			# 	"Request timed out; Skipping and going to next run...\n";
			# 	next;
			# }
			my $sequencing_data = make_request($client,$sequencing_query); #decode_json $sequencing_response;
			my $sequencing_url = $sequencing_data->{results}->[0]->{url};
			print STDERR "$sequencing_url\n";
			$projects{$sequencing_url}++;
			#next if $status_only;
			#print STDERR "SU:$sequencing_url\n";
			$sequencing_url =~/(\d+)\/$/;
			my $sequencing_id = $1;
			print STDERR $r->{run_accession},"\t",$r->{instrument_platform},"\t",$r->{library_strategy},"\n";
			print STDERR "base count:\t",$r->{base_count},"\n";
			print STDERR "read count:\t",$r->{read_count},"\n";
			my $readsresp = make_request($client,"$erga_status_url/enareads/?project=". $sequencing_id );
			#$client->GET("$erga_status_url/reads/?project=". $project_id);
			my $reads_url = '';
			if ($readsresp->{count} == 0) {
				#reads record doesn't exist. Need to insert it.
				my %read_rec = ();
				$read_rec{'project'}=$sequencing_url;
				make_post($client,"$erga_status_url/enareads/", encode_json \%read_rec);
				my $readsresp2 = make_request($client,"$erga_status_url/enareads/?project=". $sequencing_id);
				$reads_url = $readsresp2->{results}->[0]->{url};
			}else{
				$reads_url = $readsresp->{results}->[0]->{url};
			}
			
			my $read_type = '';
			my $library_strategy  = $r->{library_strategy};
			my $instrument = $r->{instrument_platform};
			#print STDERR "$instrument $instrument\n";
			if ($library_strategy =~ /RNA-?Seq/i){$read_type = "RNA";$library_strategy = "RNA-Seq";}
			if ($instrument =~ /ILLUMINA/i && $library_strategy =~  /WGS/i){$read_type = "Illumina";$library_strategy = "WGS";}
			if ($instrument =~ /PACBIO/i){$read_type = "HiFi";$library_strategy = "WGS";}
			if ($instrument =~ /ILLUMINA/i && $library_strategy =~ /Hi-?C/i){$read_type = "HiC";$library_strategy = "Hi-C";}
			if ($instrument =~ /OXFORD_NANOPORE/i && $library_strategy =~ /WGS/i){$read_type = "ONT";$library_strategy = "WGS";}


			my %run_insert_data = ();
			$run_insert_data{project}=$sequencing_url;
			$run_insert_data{read_type}=$read_type;
			$run_insert_data{seq_yield}=$r->{base_count};
			$run_insert_data{num_reads}=$r->{read_count};
			$run_insert_data{biosample_accession}=$r->{'sample_accession'};
			$run_insert_data{run_accession}=$r->{'run_accession'};
			$run_insert_data{experiment_accession}=$r->{'experiment_accession'};
			$run_insert_data{study_accession}=$r->{'study_accession'};
			$run_insert_data{library_construction_protocol}=$r->{'library_construction_protocol'};
			$run_insert_data{submitted_md5}=$r->{'submitted_md5'};
			$run_insert_data{last_updated}=$r->{'last_updated'};
			$run_insert_data{reads}=$reads_url;
			my $runinsert = encode_json \%run_insert_data;
			#print STDERR "$runinsert\n" if $read_type eq "RNA";
			my $response_reads = make_request($client,"$erga_status_url/ena_run/?run_accession=".$r->{'run_accession'});
			if ($response_reads->{count} > 0) {
				#PATCH
				print STDERR "Updating existing ENA run record... \n" if $verbose;
				my $run_url = $response_reads->{results}->[0]->{url};
				make_patch($client,$run_url, $runinsert);
			}else{
				#POST
				print STDERR "Inserting new ENA run data... \n" if $verbose;
				make_post($client,"$erga_status_url/ena_run/", $runinsert);
			}

			my $reads_record = {};
			if ($r->{instrument_platform} eq 'OXFORD_NANOPORE'){
				$reads_record->{ont_ena} = $r->{experiment_accession};
				$reads_record->{study_accession} = $r->{study_accession};
			}
			if ($r->{instrument_platform} eq 'PACBIO_SMRT'){
				$reads_record->{hifi_ena} = $r->{experiment_accession};
				$reads_record->{study_accession} = $r->{study_accession};
			}
			if ($r->{instrument_platform} eq 'ILLUMINA' and $r->{library_strategy} eq 'WGS'){
				$reads_record->{short_ena} = $r->{experiment_accession};
				$reads_record->{study_accession} = $r->{study_accession};
			}
			if ($r->{instrument_platform} eq 'ILLUMINA' and $r->{library_strategy} eq 'RNA-Seq'){
				$reads_record->{rnaseq_ena} = $r->{experiment_accession};
				$reads_record->{study_accession} = $r->{study_accession};
			}
			if ($r->{instrument_platform} eq 'ILLUMINA' and $r->{library_strategy} eq 'Hi-C'){
				$reads_record->{hic_ena} = $r->{experiment_accession};
				$reads_record->{study_accession} = $r->{study_accession};
			}
			$reads_record->{project} = $sequencing_url;
			my $insert = encode_json $reads_record;
			print STDERR "$insert\n";
			my $reads_query = "$erga_status_url/enareads/?project=$sequencing_id";
			my $reads_response = "";
			for (my $i=0; $i<10; $i++){
				$client->GET($reads_query);
				$reads_response = $client->responseContent();
				last if $reads_response !~ /timeout/;
				sleep 1;
			}
			if ($reads_response =~ /timeout/){
				"Request timed out; Skipping and going to next run...\n";
				next;
			}

			my $reads_data = decode_json $reads_response;
			if ($reads_data->{count} > 0) {
				sleep 0.2;
				$client->PATCH($reads_data->{results}->[0]->{url}, $insert);
			}else{
				sleep 0.2;
				$client->POST("$erga_status_url/enareads/", $insert);
			}
		}
	}
}

print STDERR "Now updating status...\n";
#print Data::Dumper->Dump([%projects]),"\n";
exit if ! scalar keys %projects;
foreach my $surl (keys %projects){
	print STDERR "$surl\n";
	#my $sequencing_query = "$erga_status_url/sequencing/";
	#my $project_resp = make_request($client,$sequencing_query);
	#foreach my $r (@{$project_resp->{results}}){
	my $r = make_request($client,$surl); #sequencing project url
		print STDERR Data::Dumper->Dump([$r]); #$r->{species}->{scientific_name},"\n";
		my $species_response = make_request($client,$r->{species});
		my $gs_update = $species_response->{'genome_size_update'};
		next if !$gs_update;
		print STDERR $species_response->{'scientific_name'},":\t",$gs_update,"\n";
		my $project_url = $r->{url};
		$project_url =~/(\d+)\/$/;
		my $project = $1;
		my $runs = make_request($client,"$erga_status_url/ena_run/?project=$project");
		my %sums = ();
		foreach my $run (@{$runs->{results}}){
			if ($run->{seq_yield} > 0){
				print STDERR $run->{read_type},"\t",$run->{seq_yield},"\n";
				$sums{$run->{read_type}}+=$run->{seq_yield};
			}
		}
		my $p_response = make_request($client,"$project_url");
		my $recipename = $p_response->{recipe};
		my $r_response = make_request($client,"$erga_status_url/recipe/?name=$recipename");
		my $hifi_target = $r_response->{results}->[0]->{hifi_target};
		my $ont_target = $r_response->{results}->[0]->{ont_target};
		print STDERR Data::Dumper->Dump([$r_response->{results}->[0]]);
		my $short_target = $r_response->{results}->[0]->{short_target};
		my $hic_target = $r_response->{results}->[0]->{hic_target};
		my $rna_target = $r_response->{results}->[0]->{rna_target} * 1000000;
		my %seq_insert_data =();
		my $makechange = 0;
		if ($hifi_target>0 && $sums{HiFi}/($hifi_target * $gs_update)  > 0.8){
			$seq_insert_data{long_seq_status}="Submitted";
			$makechange=1;
		}elsif($hifi_target>0 && $sums{HiFi}/($hifi_target * $gs_update) > 0){
			$seq_insert_data{long_seq_status}="Sequencing" unless $r->{long_seq_status} eq "Done";
			$makechange=1;
		}
		print STDERR join("\t",($ont_target,$sums{ONT},$gs_update)),"\n";
		if ($ont_target>0 && $sums{ONT}/($ont_target * $gs_update)> 0.8){
			$seq_insert_data{long_seq_status}="Submitted";
			$makechange=1;
		}elsif($ont_target>0 && $sums{ONT}/($ont_target * $gs_update)> 0){
			$seq_insert_data{long_seq_status}="Sequencing" unless $r->{long_seq_status} eq "Done";
			$makechange=1;
		}
		print STDERR join("\t",($short_target,$sums{Illumina},$gs_update)),"\n";
		if ($short_target>0 && $sums{Illumina}/($short_target * $gs_update)> 0.8){
			$seq_insert_data{short_seq_status}="Submitted";
			$makechange=1;
		}elsif($short_target>0 && $sums{Illumina}/($short_target * $gs_update)> 0){
			$seq_insert_data{short_seq_status}="Sequencing" unless $r->{short_seq_status} eq "Done";
			$makechange=1;
		}
		print STDERR join("\t",($hic_target,$sums{HiC},$gs_update)),"\n";
		if ($hic_target>0 && $sums{HiC}/($hic_target * $gs_update)> 0.8){
			$seq_insert_data{hic_seq_status}="Submitted";
			$makechange=1;
		}elsif($hic_target>0 && $sums{HiC}/($hic_target * $gs_update)> 0){
			$seq_insert_data{hic_seq_status}="Sequencing" unless $r->{hic_seq_status} eq "Done";
			$makechange=1;
		}
		print STDERR "RNA target:",$rna_target,"\n";
		if ($rna_target>0 && $sums{RNA}/$rna_target > 0.8){
			$seq_insert_data{rna_seq_status}="Submitted";
			$makechange=1;
		}elsif($rna_target>0 && $sums{RNA}/$rna_target > 0){
			$seq_insert_data{rna_seq_status}="Sequencing"  unless $r->{rna_seq_status} eq "Done";;
			$makechange=1;
		}
		if ($makechange){
			my $seqinsert = encode_json \%seq_insert_data;
			make_patch($client,$project_url,$seqinsert);
		}

	#}			
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
      last if $response !~ /<html/;
      sleep 5;
    }
    if ($response =~ /timeout/){
      return 0;
    }elsif ($response =~ /<html/){
      print STDERR "$response\n";
      return 0;
    }elsif ($response =~ /Error/){
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
      last if $response !~ /<html/;
      sleep 5;
    }
    if ($response =~ /timeout/){
      return 0;
    }elsif ($response =~ /<html/){
      print STDERR "$response\n";
      return 0;
    }elsif ($response =~ /Error/){
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
      last if $response !~ /<html/;
      sleep 5;
    }
    if ($response =~ /timeout/){
      return 0;
    }elsif ($response =~ /<html/){
      print STDERR "$response\n";
      return 0;
    }elsif ($response =~ /Error/){
      print STDERR "$response\n";
      return 0;
    }else{
      return decode_json $response;
    }
}