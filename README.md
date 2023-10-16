# reptor (alpha version)
reptor allows you to automate pentest reporting with SysReptor.

 * Create findings and notes from tool outputs
 * Upload evidences (also bulk upload)
 * Import data from other reporting tools

**GitHub:** [https://github.com/Syslifters/reptor/](https://github.com/Syslifters/reptor/){ target=_blank }  
**Docs:** [https://docs.sysreptor.com/cli/getting-started](https://docs.sysreptor.com/cli/getting-started){ target=_blank }   
**Setup:** [https://docs.sysreptor.com/cli/setup](https://docs.sysreptor.com/cli/setup){ target=_blank }   
**PyPi:** [https://pypi.org/project/reptor/](https://pypi.org/project/reptor/){ target=_blank }   


## Usage

```usage: reptor [-h] [-s SERVER] [-t TOKEN] [-k] [-p PROJECT_ID]
              [--private-note] [-f] [-v] [--debug] [-n NOTETITLE]
              [--no-timestamp] [--file FILE]

Examples:
                reptor conf
                echo "Upload this!" | reptor note
                reptor file data/*
                cat sslyze.json | reptor sslyze --json --push-findings
                cat nmap.xml | reptor nmap --xml --upload

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity (> INFO)
  --debug               sets logging to DEBUG
  -n NOTETITLE, --notetitle NOTETITLE
  --no-timestamp        do not prepend timestamp to note
  --file FILE           Local file to read

subcommands:
  
  Core:
   plugins               Allows plugin management & development
   conf                  Shows config and sets config
  
  Projects & Templates:
   template              Queries Finding Templates from reptor.api
   project               Work with projects
   translate             Translate Projects to other languages via Deepl
   projectfindings       Export your project findings as a summary or checklist
  
  Uploads:
   file                  Uploads a file
   finding               Uploads findings from JSON or TOML
   note                  Uploads and lists notes
  
  Tools:
   nmap                  format nmap output
   zap                   Parses ZAP reports (JSON, XML)
   sslyze                format sslyze JSON output
  
  Importers:
   importers             Show importers to use to import finding templates
   ghostwriter           Imports GhostWriter finding templates

configuration:
  -s SERVER, --server SERVER
  -t TOKEN, --token TOKEN
                        SysReptor API token
  -k, --insecure        do not verify server certificate
  -p PROJECT_ID, --project-id PROJECT_ID
                        SysReptor project ID
  --private-note        add notes to private notes
  -f, --force-unlock    force unlock notes

```