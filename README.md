# JSON Directory Sorter

!Project still in development as I've yet to make it write to the directory.json
!Alongside tidying up the code as well

This project is for building a JSON file to be used
on my portfolio website, allowing data and other websites
to be searched through to find information

# Overview

The project is built in python using tkinter and a JSON 
package. It takes in 4 inputs, 2 from a dropdown menu
And compares it to current information within that section.
If none are found, it is placed in the JSON file.

The JSON file comparitor is built for taking 4 inputs (name, description, section & subsection) and using these to create a json input. 
The program reads the data of the JSON, including 3 most recent additions, total entries and populates the section dropdown.
Once the user attempts to verify and add, several checks take place, being:
Sanitising and normalising the input (ensuring there is a https, https, ftp or www.)
Checking if the URL is an exact match (if it is, an error message appears, and points to which category)
Check if there are similar matches

Any similar matches are brought up, and the user is asked to confirm if they are happy to proceed.
If the user is happy, it is added to the JSON file, along with a success or error message, depending on outcome.
The program then clears the fields, allowing for additional inputs without having to manually clear the fields 

The program allows for customisation, as the categories can be manually changed in the code, as well as subsections

# What i learned
I learned several aspects, broken down below
GUI - This is the first project i have built, from scratch, that uses a graphical user interface to show data
AI assistance - The program allowed for me to use AI assistance, helping to speed up programming along with having to use my own intelligence to help debug any potential problems
JSON - While i have an understanding of JSON, it helped me to gain a better understanding of CRUD when handling data, specifically Create Read Update

# What real world problem did it solve?
The program helped me solve a real world problem with my portfolio website. I wanted to add a section where the user could obtain an educational link, and pick which ones. The website would take the JSON and output several, that may interest them.
This allowed me to add an additional dimension to my portfolio website, looking at what ways can i stand out, even if they are subtle.