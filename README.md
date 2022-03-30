# transcripts

This contains a Python script to summarize student performance in specific
subjects. It was created to aid in selecting candidates for the
KME Math Honor Society at LIU Post, but the script could 
be repurposed pretty easily. 

## Description
The input `file` is a single .pdf of unofficial transcripts from a collection of students, most likely in similar majors. 
Course subject codes, e.g. `["MTH", "PHY"]`, are given by a global variable in transcripts.py, along with courses that
should be excluded from counting as "upper-level."  The primary function `analyze_transcripts(file, output_file="TranscriptSummary.xlsx")`
then determines the courses/grades from the specified subjects for each student, calculates information about the "upper-level" courses completed (number of courses completed, gpa of those courses, number in progress), returns this information as a Pandas DataFrame, and saves it as an Excel spreadsheet.

It was written to handle LIU Post
unofficial transcripts, so the scraping likely needs to be modified in order to work with transcripts from other sources.

## Usage
Create a single .pdf file of unofficial transcripts (from LIU Post), and place the `file` in the subdirectory `"data/"` (or `IN_DIR` if modified).

In transcripts.py update:
- `CURR_SEM` : the current semester, eg "S21" for Spring 2021
- `SUBJECTS` : list of subject codes for courses to find
- `IGNORE_COURSES` : courses to omit when calculating information about "upper-level courses"

If using an interactive IDE (eg Spyder, Jupyter), run the entire file transcripts.py and then run the commands:
```
file = "Transcripts-S21.pdf"
df = analyze_transcripts(file)  # default output file, or 
df = analyze_transcripts(file, "Awards-S21.xlsx")  # specified output
```
If desired, one can further work with the information as the returned Pandas DataFrame `df`. 

If using a terminal window, run either of the commands:
```
python transcript_runner.py "Transcripts-S21.pdf"
python transcript_runner.py "Transcripts-S21.pdf" "Awards-S21.pdf"
```

In both cases, the spreadsheet will be saved in the subdirectory `"data/"` (or `OUT_DIR` if modified). The carrot ^ in column titles is to denote "upper-level," eg `MTH^ GPA` is the GPA for completed upper-level math courses.
