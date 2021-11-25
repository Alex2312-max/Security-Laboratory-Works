# Security-Laboratory-Works

### Laboratory Work 1:

Created a GUI:

  - Commands: Open File, Save, Save As, Copy, Cut, Undo, Redo, Paste;
  - Parsing function based on regex

Reading the audit file:
<img src='data/read_audit.png'>


Save json:
<img src='data/save_json.png'>
<img src='data/save_json_directory.png'>


Confirming the results by checking the json file in a json viewer online:
<img src='data/json_check.png'>


### Laboratory Work Nr. 3

Audit file check:

![image](https://user-images.githubusercontent.com/55151032/142918137-c68aa4fc-1ab7-4ef3-865a-604ae7082f1e.png)

Code snippet:

![image](https://user-images.githubusercontent.com/55151032/142919196-72466a90-ad56-43c0-acc6-7f811731df6a.png)

  Also, there is the logic in the scrips main.py you can find the whole logic behind Audit Workstation Page
  that is too big to be included in here.
  

### Laboratory Work Nr. 4 and 5

Audit policies enforce:

![image](https://user-images.githubusercontent.com/55151032/143426963-87db08e0-20e7-43e0-b60c-bf4180bab377.png)

  Here, the process of checking occurs, we compare the results between the 'expected' output and real output, and see that this policies 
  were not right.
  
![image](https://user-images.githubusercontent.com/55151032/143427258-4262d64a-b17f-48c4-b4e8-67cfd2fca211.png)
  
  I added some commands before, new keys and values in the dictionary before recording the video due to the process being too long.
  And by using this commands we can enforce the policies. Also, we can see the functionality of the 'Rollback' button, by checking the
  needed policies, and introducing the new key-value pair in the dictionary 'unload', we can rollback to previous settings and this will
  be shown by changing in colors, for green the policie is installed and for red it is not installed.

