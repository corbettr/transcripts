#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Corbett Redden
Python script to summarize student performance in specific
subjects. Created to aid in selection of candidates for 
KME Math Honor Society at LIU Post, but the program could 
be repurposed pretty easily. It is written to handle LIU Post
unofficial transcripts, so the scraping will likely need to be
modified to work with transcripts in other formats.

Primary function is: analyze_transcripts(file, output_file)
Input pdf lives in subdirectory 'data' (or IN_DIR if modified)

To operate, run entire file within interactive IDE
(eg Spyder, Jupyter) and then run commands:
>>> file = "Transcripts-S21.pdf"
>>> df = analyze_transcripts(file)
or
>>> df = analyze_transcripts(file, "Awards-S21.xlsx")

or 

in terminal window run command:
>>> python transcript_runner.py "Transcripts-S21.pdf"
or
>>> python transcript_runner.py "Transcripts-S21.pdf" "Awards-S21.xlsx"
"""

import re
import os
import numpy as np
import pandas as pd
import pdfplumber  # pip install pdfplumber
from natsort import natsorted  # pip install natsort


# Global variables are designed to be modified.
CURR_SEM = "S22"  # eg "F20" or "Sum19" or "S21"
SUBJECTS = ["MTH", "PHY"]
# IGNORE_COURSES must include key for every subject.
# To not exclude any courses in summary, use { "MTH" : set() }
IGNORE_COURSES = {
    "MTH" : {"MTH 1", "MTH 3", "MTH 4", "MTH 5", "MTH 6", "MTH 15", "MTH 16",
             "MTH 19", "MTH 90"},
    "PHY" : {"PHY 3", "PHY 4"},
    }

IN_DIR = "data"  # subdirectory for inputs
OUT_DIR = "data"  # sudirectory for outputs

# Can be changed, but it would be unlikely
GPA_VAL = {
    "A":4.0, "A-":3.667, "B+":3.333, "B":3.0, "B-":2.667,
    "C+":2.333, "C":2.0, "C-":1.667, "D":1.0, "F":0.0
    }

            
def analyze_transcripts(file, output_file="TranscriptSummary.xlsx"):    
    """
    Given a single pdf of transcripts (eg transcripts of all
    math majors), create a dataframe and spreadsheet summarizing
    student performance in all courses of specified subjects.
                                       
    Parameters
    ----------
    file : string (name of input .pdf file)
        DESCRIPTION. (Multiple) transcripts printed as single pdf.
        located in subdirectory IN_DIR='data'
    output_file : string (name of output .xlsx file)
        DESCRIPTION. The default is "TranscriptSummary.xlsx",
        located in subdirectory OUT_DIR='data'

    Returns
    -------
    df : Pandas DataFrame
        DESCRIPTION. df used to create spreadsheet
    """  
    raw_text = scrape_pdf(os.path.join(IN_DIR, file))
    one_space_text = remove_extra_spaces(raw_text)
    transcripts =  separate_students(one_space_text)
    df = transcript_data(transcripts)
    if output_file:
        df.to_excel(os.path.join(OUT_DIR, output_file), na_rep="")
    return df


def scrape_pdf(file):
    """ Given pdf file (multipage), return all text as string. """
    text = "\n"
    
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
            text += "\n"
            page.close()
            
    return text
        

def remove_extra_spaces(text):
    return re.sub(" + *", " ", text)


def separate_students(text, name_splitter="Name : ", name_ret=False):
    """
    Input: text (str) - usually multiple transcripts as single str
    Return: transcripts (list of strings, each entry one transcript)
    When name_ret=True, also return list of names.
    """    
    names = re.findall(name_splitter+"(.*)\n", text)

    transcripts = re.split(name_splitter, text)
    del transcripts[0]

    for i in range(len(transcripts)):
        transcripts[i] = name_splitter + transcripts[i]
    
    if name_ret:
        return (transcripts, names)
    else:
        return transcripts


def transcript_data(transcripts, creds=dict()):
    """
    Input: transcripts (list of strings, each entry one transcript)
    Optional input: creds (dictionary of credits for courses)
    
    Extract data from each transcript, and 
    return as Pandas DataFrame
    """
    records_list = []
    
    for transcript in transcripts:
        data_dict = personal_info(transcript)
        for subj in SUBJECTS:
            subj_grades = grades_of_subj(transcript, subj, creds)
            data_dict.update(subj_grades)
            data_dict.update(subj_summary(subj, subj_grades, creds))
        records_list.append(data_dict)        
        
    subj_summ_cols = list()
    for subj in SUBJECTS:
        subj_summ_cols += [f"Num {subj}^ courses", f"{subj}^ GPA", 
                           f"Num {subj}^ now"]

    return pd.DataFrame(
        records_list,
        columns = ["Name", "Student_ID", "Plan"]
                 +["Sex", "Address1", "Address2", "Address3"]
                 + subj_summ_cols
                 + natsorted(creds)
        )


def subj_summary(subj, subj_grades, creds):
    """
    Input: subj (string), subj_grades (dict), creds (dict)
    Return: summary (dict)
    Calculate summary info on grades for one subject, but
    only for courses: completed, with letter grade, and 
    not in the IGNORE_COURSES.
    Note: subj_grades is assumed to be {subj xx:grade} for 
    one individual student.
    """
    courses_to_count = [course for course in subj_grades 
                        if (course not in IGNORE_COURSES[subj] and
                        subj_grades[course] in GPA_VAL)]
    num_taken = len(courses_to_count)
    creds_taken = sum([creds[course] for course in courses_to_count])
    gpa_creds = sum([GPA_VAL[subj_grades[course]]*creds[course] 
                     for course in courses_to_count])
    if creds_taken > 0:
        gpa = gpa_creds/creds_taken
    else:
        gpa = np.nan
    num_in_progress = sum([ 1 for course in subj_grades 
                           if course not in IGNORE_COURSES[subj] and
                           subj_grades[course]==CURR_SEM ])
    return {
        f"Num {subj}^ courses" : num_taken,
        f"Num {subj}^ creds" : creds_taken,
        f"{subj}^ GPA" : gpa,
        f"Num {subj}^ now" : num_in_progress
        }
    

def personal_info(transcript):
    """ input transcript (string), return dict """
    name = re.findall("Name : (.*)\n", transcript)[0]
    student_id = re.findall("Student ID: (.*)\n", transcript)[0]
    sex = re.findall("Sex : (.*)\n", transcript)[0]
    address = re.findall("Address : (.*)\n (.*)\n (.*)\n", transcript)
    if address: 
        address1 = address[0][0]
        address2 = address[0][1]
        address3 = address[0][2]
    else: 
        address1 = ""
        address2 = ""
        address3 = ""
        
    return {
        "Name" : name,
        "Student_ID" : student_id,
        "Sex" : sex,
        "Address1" : address1,
        "Address2" : address2,
        "Address3" : address3
        }

    
def grades_of_subj(transcript, subj, creds={}):
    """
    Given transcript (string), subj (string), and creds (dictionary
    of credit values for courses, usually being maintained throughout
    runs over multiple transcripts), return a dictionary of {course:grade}
    for all courses in given subj appearing in transcript.
    Also extracts student's Plan (major) from final value.
    
    eg return {'MTH 9':'A-', 'MTH 22':'S21'}
    creds now contains {'MTH 9':4.00, 'MTH 22':3.00}
    """
    grades_dict = dict()
    # semester_split should look something like
    # [trash, 'Fall 2018', F18_transcript, 'Spring 2019', S19_transcript]
    semester_split = re.split(
        "(Fall 20..|Spring 20..|Summer 20..|Winter 20..)", transcript)
    if len(semester_split)%2 != 1:
        raise Exception("Splitting by semesters went wrong.")    
    
    plan = re.findall("Plan : (.*)\n", semester_split[-1])
    if plan:
        grades_dict["Plan"] = plan[0]

    for i in range(len(semester_split)//2):
        semester = semester_split[2*i+1]
        info = semester_split[2*i+2]
        raw_grades = re.findall(subj + " .* [0-9]\.[0-9][0-9].*\n", info)

        for line in raw_grades:
            course_num = re.findall(subj + " ([0-9]+[A-Z]?|NE) ", line)[0]
            course = f"{subj} {course_num}"

            if course not in creds:
                num_creds = re.findall("[0-9]\.[0-9][0-9]", line)[0]
                creds[course] = float(num_creds)
                
            grade = re.findall(
                "[0-9]\.[0-9][0-9] [0-9]\.[0-9][0-9] ([A-Z]\+?\-?)", line)
            if grade: 
                grade = grade[0]
            else:
                grade = sem_abbr(semester)
            
            grades_dict[course] = grade

    return grades_dict
    
    
def sem_abbr(semester):
    """ Abbreviates semester (string), eg 'Fall 2021' becomes 'F21' """    
    sem = re.sub("20([0-9][0-9])", r"\1", semester)
    sem = re.sub("Fall ", "F", sem)
    sem = re.sub("Spring ", "S", sem)
    sem = re.sub("Summer ", "Sum", sem)
    sem = re.sub("Winter ", "Win", sem)
    return sem
