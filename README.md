# WebEnum
WebEnum is a GUI Web Scanner used to automate all of the simple, but time consuming, tasks that are often encountered in Capture the Flag (CTF) challenges. WebEnum only completes basic fuzzing and has no auto-exploitation, keeping it in line with the rules of OSCP. Additionally, this makes it more ideal for presenting learning opportunities while saving time.

![alt text](https://github.com/Ayodub/WebEnum/blob/main/images/loading_screen.png?raw=true)

WebEnum takes a list.txt of URL directories. This list should be generated with Dirsearch, Gobuster, or a similar tool. It will then perform a number of tasks:

- Crawler: WebEnum starts at the URLs given and begins crawling the website. This ensures that oddly named directories which will have been missed by directory brute forcing are added to the list. Naming a directory something odd is a common trick that CTF developers use, and manually sifting through every directory is time consuming. Any new pages found will be added to list.txt

- Comments: WebEnum will take the list created and extract all commented code from the pages. This saves time from manually looking through source code which, again, is a typical trick that some CTF room developer use. This is something most CTF players find irritating and can waste a lot of time checking source code 'just in case'. Now a quick scroll through a curated list will confirm if there are any hidden clues.

- Command Injection: WebEnum will perform very simple command injection fuzzing in forms and URL parameters. There is no auto-exploitation, and it only checks for the simplest payloads. This is simply meant to save time from manually testing simple payloads in every form and URL parameter. If a command seems successful it will then be up to the user to find out how to exploit this.

- Local File Inclusion: Simple enumeration of URL parameters looking for the /etc/passwd file. This is tested with a simply payload list containing different path lengths and encodings.

- SQL Injection: Simple enumeration of forms and URL parameters for error based, time based, and blind SQL injections. This fuzzer does not attempt deeper enumeration or exploitation of vulnerabilities, but simply confirms if there may be a vulnerability at one of the input fields.

- XSS Injection: WebEnum will search for simple Stored Cross Site Scripting vulnerabilities. This fuzzer is extremely basic and does not have much use in CTF environments.


![alt text](https://github.com/Ayodub/WebEnum/blob/main/images/interface.png?raw=true)


Usage:

pip install -r requirements.txt

Save URLs to a file named list.txt, each separated by a single line. Directory buster tools usually have a switch to allow you to save the output as a simple list.

Import the URL into the GUI on the home tab.

Press 'Start Crawling'.
