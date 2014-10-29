#!/usr/bin/perl -w
#
# $Id: extractbib.pl 1057 2014-01-21 09:44:50Z klugeflo $
#
# based on extractbib.pl v1.0 by Xiaoquan (Michael) Zhang
# see http://mikezhang.com/extractbib/extractbib.txt
#
# This script is able to handle multiple .tex and .bib files
# NOTE: bibtex entries must terminate with a closing '}' as single character
# in a separate line

# Usage: ./extractbib.pl -t texfiles -b bibfiles [-o output.bib]

################################################################################

use v5.10.1;


if (@ARGV <4){
    print "At least four arguments are needed. Write $0 -h for help\n";
    usage();
    exit;
}

our @texfiles;
our @bibfiles;
my $outfile;

our @references; # stores bib references
our @bibliography; # stores all bibtex files

$err = parseArgs();
if ($err != 0) {
    print "An error occurred while parsing arguments: $err\n";
    exit 1;
}

print "Texfiles: @texfiles\n";
print "Bibfile: @bibfiles\n";

if (defined $outfile) {
    print "Outfile: $outfile\n";
}
else {
    print "Using STDOUT for output\n";
}

for $texfile (@texfiles) {
    readTexFile($texfile);
}

@references = sort @references;
$nrefs = @references;

print "Found $nrefs distinct references: @references\n";

for $bib (@bibfiles) {
    open (BIB, $bib) or die ("Could not open $bib: $!");
    my @row=<BIB>;
    close (BIB);
    push(@bibliography, @row);
}

$biblen = @bibliography;
print "Bibliography has $biblen lines\n";

$thebib = extract();
#print $thebib;

if (defined $outfile) {
    open (OUT, ">$outfile") or die("Cannot open the output file $out: $!");
    print OUT "$thebib";
    close (OUT);    
}
else {
    print $thebib;
}


exit;

################################################################################

sub parseArgs {
    use constant {
	STATE_NONE => 0,
	STATE_TEX => 1,
	STATE_BIB => 2,
	STATE_OUT => 3,
	STATE_FOO => 4,
    };
    my $state = STATE_FOO;
    my $error = 3;
    foreach $arg (@ARGV) {
	if ($arg=~/^-\S/) {
	    for ($arg) {
		when (/^-t/) { $state = STATE_TEX }
		when (/^-b/) { $state = STATE_BIB }
		when (/^-o/) { $state = STATE_OUT }
		when (/^-h/) { 
		    usage();
		    exit;
		}
		default {
		    print "Unknown switch $arg\n";
		    $error |= 4;
		}

	    }
	}
	else {
	    if ($state == STATE_TEX) {
		push(@texfiles, $arg);
		$error &= ~1;
	    }
	    elsif ($state == STATE_BIB) {
		push(@bibfiles, $arg);
		$error &= ~2;
	    }
	    elsif ($state == STATE_OUT) {
		$outfile = $arg;
		$state = STATE_NONE;
	    }
	    else {
		print "Stray argument $arg\n";
		$error |= 8;
	    }
	}
    }
    return $error;
}

################################################################################

sub readTexFile {
    $tex = shift;
    print "Now reading tex file $texfile...\n";

    open (TEX, $tex) or die ("Could not open $tex: $!");
    my @row=<TEX>;
    close (TEX);
    
    my $save;
    my $state=0; #state=1 means a multi-line citation is in action
    foreach $line (@row){
	next if ($line=~/^\s*%/) ; #skip comment lines
	if ($state){
	    $save=$save.$line;
	    $line=$save;
	}
    
	if ($line=~/\\cite/ &&!($line=~m/\\cite([^}]*){([^}]*)}/)){
	    $state=1;
	    $save=$line;
	    next;
	}
	
	while ($line=~m/\\cite([^}]*){([^}]*)}/g) {
	    $state=0;
	    my $cite=$2;
	    if ($cite =~ /,/){ 
		my @names = split(/,/, $cite);
		my $names=@names;
		for (my $i=0; $i<=$names-1; $i++){
		    compare($names[$i]);
		}
	    } else {
		compare($cite);
	    }
	    
	} 
    }
}

################################################################################

sub extract {
    my $out;
    $references=@references;
    print "\% Total Number of Citations: $references\n";
    for (my $i=0; $i<=$references-1; $i++) {
	my $found=0;
	my $line;
	foreach $line (@bibliography) {
	    if (($found<2)) {
		if ($line=~m/{\s*$references[$i],/i) {
		    $found=1;
		    $out .= $line;
		}
		elsif ($found==1) {
		    $out .= $line;
		    if ( ($line=~m/^}/)) {
			$out .= "\n";
			$found=2;
		    }
		}
	    }
	}
    }
    return $out;
}

################################################################################

sub compare {
    my $cite=shift;
    $cite=~ s/^\s+//;
    $cite=~ s/\s+$//;
    @match=grep(/$cite/i, @references);
    $match=@match;
    if ($match == 0){
	push(@references, $cite);
    }
}

################################################################################

sub usage {
    print<<EOF;
  Usage: $0 -t [texfiles] -b [bibfiles] -o [outfile.bib]
      Extracts all bibtex entries from .bib files that appear in the .tex files.
      if -o is omitted, output is written to stdout
      if [outfile.bib] exists, it will be overwritten
EOF
}

################################################################################
