#!/usr/bin/env perl

use DBI;
use Mysql;
# get the 3+ hours of work i did on 03.03.01
require "tMG_constants.pl";

# make the browser happy
print   "Content-type: text/html\n\n";       
print   "<body> <font face=\"sans-serif\">";


#This part translates the input from the form and makes it readable
#You can ignore this part
#----------------------------------------------------------------------

#decode html parameterstuff
@keys_vals = split(/&/,$ENV{QUERY_STRING});
%FORM = undef;
foreach $key_val (@keys_vals){
  ($key,$value) = split(/=/,$key_val);
  $value =~ tr/+/ /;
  $value =~ s/%([\dA-Fa-f][\dA-Fa-f])/pack ("C", hex($1))/eg;
  $FORM{$key} = $value;
}

$dbh = DBI->connect("DBI:mysql:tmg:mysql.themountaingoats.net","<TMG_USER>","<TMG_PASSWD>");

if($FORM{ACTION} eq ""){
	print "<h1>Shows In Database...</h1><hr>\n";
	$sql = "select * from shows order by date";

	$sth = $dbh->prepare($sql) or die("Can't do prepare: $dbh->errstrn");
	$rv = $sth->execute() or die("Can't execute SQL: $sql [$dbh->errstrn]");

	print "<ul>\n";
	while(@row = $sth->fetchrow_array) {
		$SHOWID = $row[$dbSHOWID];
		print "<li><a href=\"http://www.themountaingoats.net/cgi-bin/songs.cgi?ACTION=show_set&SHOWID=$SHOWID\">$row[0] -  $VENUE_TITLES[$row[1]]</a>\n";
	}
	print "</ul>\n";
	$sth->finish;
}
elsif($FORM{ACTION} eq "show_set"){
	$sql = "select * from shows where SHOWID = $FORM{SHOWID}";

	$sth = $dbh->prepare($sql) or die("Can't do prepare: $dbh->errstrn");
	$rv = $sth->execute() or die("Can't execute SQL: $sql [$dbh->errstrn]");
	while(@row = $sth->fetchrow_array) {
		print "<title>the Mountain Goats setlist from $row[0]</title>\n";
		print "<h1>$row[0] - $VENUE_TITLES[$row[1]]</h1><hr>\n";
		if($row[72] ne ""){
			print "<h3>Pics:</h3>\n";
			@pics = split(/\|/,$row[72]);
			@piccaps = split(/\|/,$row[73]);
			print "<table border=0>\n";
			print "<tr><th>\n";
			foreach $pic (@pics){
				print "<td align=center><img src=\"http://www.themountaingoats.net/pics/tour/$pic\" height=100>\n";
			}
			print "<tr><th>\n";
			foreach $cap (@piccaps){
				print "<td align=center>$cap\n";
			}
			print "</table>\n";
			print "<hr>\n";
		}
			$idx = $dbSONG1;
			print "<ul>\n";
			$cnt = 0;
			foreach $idx (@dbSONGS){
				last if($row[$idx] eq "");
				print "<li> <a href=\"http://www.themountaingoats.net/cgi-bin/songs.cgi?ACTION=show_song&SONGID=$row[$idx]\">$TMG_TITLES[$row[$idx]]</a>";
				$suffix = "";
				if($row[$dbNOTES[$cnt]] ne ""){
					$cur_note = $row[$dbNOTES[$cnt]];
					for($i = 0;$i< $dbMAX_NOTES;$i++){
						$suffix .= $NOTE_MARKS[$i] if(($cur_note & 1) == 1);	
						$cur_note >>= 1;
					}
				}
				print "$suffix\n";
				$cnt++;
			}
			print "</ul>\n";
			for($idx=$dbNOTE_TEXT0;$idx < $dbNOTE_TEXT4;$idx++){
				last if($row[$idx] eq "");
				$mark = $idx - $dbNOTE_TEXT0;
				print "$NOTE_MARKS[$mark] <a href=\"http://www.themountaingoats.net/cgi-bin/songs.cgi?ACTION=show_note&NOTE=$row[$idx]\">$NOTES[$row[$idx]]</a><br>\n";
			}
	}
	$sth->finish;
}
elsif($FORM{ACTION} eq "show_song"){
	# print out all the info we know about that song (shows/releases/etc)
	$sql = "select * from shows where ";
	for($i=1;$i<$MAX_SHOW_SONGS;$i++){
		$sql .= "song$i = $FORM{SONGID} or ";
	}	
	$sql =~ s/ or $//;
	$sql .= ";";
	
	$sth = $dbh->prepare($sql) or die("Can't do prepare: $dbh->errstrn");
	$rv = $sth->execute() or die("Can't execute SQL: $sql [$dbh->errstrn]");
	print "<h3>Shows $TMG_TITLES[$FORM{SONGID}] has been played at:</h3>\n";
	print "<ul>\n";
	while(@row = $sth->fetchrow_array) {
		$SHOWID = $row[$dbSHOWID];
		print "<li> <a href=\"http://www.themountaingoats.net/cgi-bin/songs.cgi?ACTION=show_set&SHOWID=$SHOWID\">$row[0] - $VENUE_TITLES[$row[1]]</a>\n";
	}
	print "</ul>\n";
	$sth->finish;
	
	print "<hr>\n";
	$sql = "select * from songs where songid = $FORM{SONGID};";
	$sth = $dbh->prepare($sql) or die("Can't do prepare: $dbh->errstrn");
	$rv = $sth->execute() or die("Can't execute SQL: $sql [$dbh->errstrn]");
	while(@row = $sth->fetchrow_array) {
		$LYRICS = $row[1];
	}
	print "<h3><a href=\"http://www.themountaingoats.net/${LYRICS}\">Lyrics</a> for $TMG_TITLES[$FORM{SONGID}]</h3>\n";
	$sth->finish;
	

	print "<hr>\n";
	print "<h3>Releases containing $TMG_TITLES[$FORM{SONGID}] </h3>\n";
	$sql = "select * from songs where songid = $FORM{SONGID};";
	$sth = $dbh->prepare($sql) or die("Can't do prepare: $dbh->errstrn");
	$rv = $sth->execute() or die("Can't execute SQL: $sql [$dbh->errstrn]");
	print "<ul>\n";
	while(@row = $sth->fetchrow_array) {
		for($album=2; $album <= 6; $album++){
			$ALBUM = $row[$album];
			if($ALBUM != -1 && $ALBUM ne ""){
				$ALBUM_NICK = $ALBUM_SH[$ALBUM];
				print "<li> <a href=\"http://www.themountaingoats.net/music/${ALBUM_NICK}.html\">$ALBUM_TITLES[$ALBUM]</a>\n";
			}
		}
	}
	print "</ul>\n";
	$sth->finish;
	
	print "<hr>\n";   
	$sql = "select * from series where song_id = $FORM{SONGID};";
	$sth = $dbh->prepare($sql) or die("Can't do prepare: $dbh->errstrn");
	$rv = $sth->execute() or die("Can't execute SQL: $sql [$dbh->errstrn]");
	print "<h3>This song belongs to the following series:</h3>\n";      
	print "<ul>\n";
	while(@row = $sth->fetchrow_array) {
		$SERIESID = $row[0];
		print "<li> <a href=\"http://www.themountaingoats.net/cgi-bin/songs.cgi?ACTION=show_series&SERIES=$SERIESID\">$SERIES_TITLES[$row[0]]</a>\n";
	}
	print "</ul>\n";
	$sth->finish;

}
elsif($FORM{ACTION} eq "show_series"){
	# print out all the songs in the series
	$sql = "select * from series where series_type = $FORM{SERIES};";
	$sth = $dbh->prepare($sql) or die("Can't do prepare: $dbh->errstrn");
	$rv = $sth->execute() or die("Can't execute SQL: $sql [$dbh->errstrn]");
	print "<h3>Songs in the \"$SERIES_TITLES[$FORM{SERIES}]\" series:</h3>\n";      
	print "<ul>\n";
	@SONGS = ();
	$count = 0;
	while(@row = $sth->fetchrow_array) {
		$SONGS[$count]{id} = $row[1];
		$SONGS[$count]{title} = $TMG_TITLES[$row[1]];
		$count++;
	}
	@SONGS_A = sort by_title @SONGS;
	foreach $song (@SONGS_A)
	{
		%tmp = %{$song};
		$SONGID = $tmp{id};
		print "<li><a href=\"http://www.themountaingoats.net/cgi-bin/songs.cgi?ACTION=show_song&SONGID=$SONGID\">$TMG_TITLES[$SONGID]</a>\n";
	}
	print "</ul>\n";
	$sth->finish;
}
elsif($FORM{ACTION} eq "show_note"){
	# print out all shows/songs that have that note
	$note = $FORM{NOTE};
	$sql = "select * from shows where note_text0=$note or note_text1=$note or note_text2=$note or note_text3=$note or note_text4=$note;";
	$sth = $dbh->prepare($sql) or die("Can't do prepare: $dbh->errstrn");
	$rv = $sth->execute() or die("Can't execute SQL: $sql [$dbh->errstrn]");
	print "<h3>Sets containg the note \"$NOTES[$note]\":</h3>\n";      
	print "[None Found]\n" if($rv == 0);
	print "<ul>\n";
	while(@row = $sth->fetchrow_array) {
		$show_date = $row[0];
		$venue = $row[1];
		$SHOWID = $row[$dbSHOWID];
		print "<li> <a href=\"http://www.themountaingoats.net/cgi-bin/songs.cgi?ACTION=show_set&SHOWID=$SHOWID\">$show_date - $VENUE_TITLES[$venue]</a>\n";
	}
	print "</ul>\n";
	$sth -> finish;
	
}

elsif($FORM{ACTION} eq "show_all_songs"){
	# print all songs alphabetically
	$sql = "select * from songs;";
	$sth = $dbh->prepare($sql) or die("Can't do prepare: $dbh->errstrn");
	$rv = $sth->execute() or die("Can't execute SQL: $sql [$dbh->errstrn]");
	$num_rows = $sth->rows;
	print "<h2>$num_rows songs found in database</h2><hr>\n";
	print "<center>\n";
	for($i = "A";$i ne "AA"; ++$i){
		printf("<a href=\"http://www.themountaingoats.net/cgi-bin/songs.cgi?ACTION=show_all_songs#label_$i\">$i</a> %s",
			($i eq "Z") ? "" : "| ");
	}
	print "</center>\n";
	print "<ul>\n";
	@SONGS = ();
	$count = 0;
	while(@row = $sth->fetchrow_array) {
		$SONGS[$count]{id} = $row[0];
		$SONGS[$count]{title} = $TMG_TITLES[$row[0]];
		$count++;
	}
	@SONGS_A = sort by_title @SONGS;
	$cur_first_letter = "A";
	foreach $song (@SONGS_A){
		%tmp = %{$song};
		$songid = $tmp{id};
		if($TMG_TITLES[$songid] ne ""){
			print "<li> <a href=\"http://www.themountaingoats.net/cgi-bin/songs.cgi?ACTION=show_song&SONGID=$songid\">$TMG_TITLES[$songid]</a>\n";
			$TMG_TITLES[$songid] =~ /^([A-Z])/;
			if($1 ne ""){
				if($1 ne $cur_first_letter){
					print "<a name=\"label_$1\"></a>\n";
					$cur_first_letter = $1;
				}
			}
		}
	}
	print "</ul>\n";
	$sth -> finish;
	
}

$dbh->disconnect;

exit(0);

sub by_title(){
	%hash1 = %{$a};
	%hash2 = %{$b};
	return $hash1{title} cmp $hash2{title};
}


