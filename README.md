# Wikipedia Crawling using selenium with Chrome

This repository provides some python scripts to crawl Wikipedia using selenium and Chrome. You should have Chrome installed on your computer.

Note: Parameters can be set in "parameters.json".


## General description

You first need to collect some Wikipedia portal/sub-portal links and store them line by line in a text file. The name of this file has to be provided using the parameter "wiki_portal_links".

Wikipedia portals gather pages related to a given topic or category.
For example, see the following portal about [Benin](https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Portail:B%C3%A9nin/Articles_li%C3%A9s).
A portal may contain several sub-portal pages. You have to provide in your "wiki_portal_links" file, page links of every single portal/sub-portal from which you want to collect Wikipedia article links.
For instance the Benin portal is divided into alphanumeric sub-portals, each one with a different link: 0-9 A.B.C.D.E.F.G.H.I.J.K.L.M.N.O.P.Q.R.S.T.U.V.W.X.Y.Z.


## Parameters description

Here is a detailed description of parameters in the json file:

	- "path_to_chome_driver" (string) : path to the chrome driver executable (default is "/usr/local/bin/chromedriver"),
	- "data_dir" (string) : name of directory in which to save the collected data (default is "data"); it is automatically created if it does not exist,
	- "results_file_name" (string) : name of csv file in which to store the data (default is "WikiPageLinks.csv"); this file is stored in the "data_dir" directory,
	- "wiki_portal_links" (string) : name of text file containing links to portal or sub-portal pages (default is "WikiPortalLinks.txt"); there must be a unique link per line,
	- "min_n_char" (integer) : minimum number of characters per page when collecting pages content (default is 30); if shorter, the page is dropped out,
	- "max_n_char" (integer) : maximum number of characters per page when collecting pages content (default is 100); if longer, only the first "max_n_char" are collected,
	- "visible_browser" ("yes"/"no") :  should the Chrome browser be visible during crawling ? (default is "no")


## Python scripts to run

	Run GetPageLinksFromWikiPortals.py to obtain a table containing Wikipedia pages titles and their links. The table is generated in the directory you indicate for "data_dir".

	Run GetNFirstChars.py to additionally obtain the content of the article pages. Articles are sorted according to their content length in a descending order.


## Docker
I provide a Dockerfile so that you can build a Docker image to run the python scripts.

	- sudo docker build --tag wiki .
	- sudo docker run -it wiki python GetPageLinksFromWikiPortals.py
	- sudo docker run -it wiki python GetNFirstWords.py
