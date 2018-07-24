# LibMaster
LibMaster is a tool that enables repeatedly using similar function blocks in different DPU configuration files. It takes **DPU libraries** and a **DPU database**, and then generates a new DPU file following an **Application plan**. Before using this tool, users should have DPU libraries with **correct standards**, which will be specified in this README.

To get the lastest update of this tool, please refer to [source code](https://github.com/jiyao94/LibMaster) on GitHub.

## Installation
To run this tool, first download or clone `source code` from GitHub. Then you need to install `Python 3.x` for whatever version or platform you use. The tool has been developed and tested under Python 3.6 32 and 64 bits for Windows, and also Python 3.5 for Linux.

After `Python 3.x` is installed, explore the source code you can find two requriements files: `requirements-linux.txt` and `requirements-win.txt`. There two specify the required pip packages you will need for the tool. You can use the following command to install them for the corresponding platform. 
```
pip install -r requirements.txt
```

Now you have finished environment setup. You can go to LibMaster folder and run `LibMaster.py` for tool with graphic UI, or run `Import.py`, `Config.py`, `Combine.py` for each part of the tool separately with command line.

### Debug mode


### Packing stand alone execution file for Windows
On Windows platform, we also provide methods to run this tool without python environment. In the `requirements-win.txt` you will install two packing tools: [Pyinstaller](http://www.pyinstaller.org/) and [cx-Freeze](http://cx-freeze.sourceforge.net/). They can package python environment into into one single execution file or a folder contains all dependencies. For detailed usage for these tools, please refer to their websites.

For **Pyinstaller**, go to `LibMaster/` directory and type command:
```
pyinstaller LibMaster.spec --clean
```
This will pack the GUI tool into one single execution file under `dist/` directory. 

For **cx-Freeze**, go to `LibMaster/` directory and type command:
```
python setup.py build
```
This will pack the GUI tool into a folder with the execution file and all the dependencies.

***Important Note:*** both packing tool don't pack "para_def.txt". You will need to copy this file into the same folder as the execution file manually for the Combine part to work. We didn't pack this file because this file is varied for different applications. See the section below for details.

## Library Standards
DPU libraries are basically DPU configuration files with specific tag and description. Each library should define inputs, outputs, and function blocks that define parameters.

For **inputs**, all the input ports should be `XPgAI` or `XPgDI`. Their output pin description should has the form `AIxxx DESCRIPTION` or `DIxxx DESCRIPTION`, where `xxx` is from 001 to 999.<br>
For **outputs**, all the output ports should be `XPgAO`, `XPgDO`, `XNetAO`, or `XNetDO`. For page outputs, their input pin description should has the form `AOxxx DESCRIPTION` or `DOxxx DESCRIPTION`. For net outputs, their tag name should be `AOxxx` or `DOxxx`, and then write the description in `Point Config`.<br>
For **function blocks**, if they has `Point Config`, their tag name should be `FBxxx` and also fill in description. But if the function block doesn't have `Point Config`, then fill the output pin description as inputs with `FBxxx`.

If the description or tag name is not following this form, the ports will not be recognized by the tool.

For a detailed example, please check `DPU01_Lib Demo3.txt` in the Example.

## Tool Instructions
This tool is consisted of three parts in order. `Import` reads standardized libraries and generates a list of inputs, outputs, and function blocks that can be parameterized. `Config` generates an **Argument file** for user to specify connections and parameters for each library accorading to the Application plan. `Combine` takes the database** and Argument file and outputs the new DPU file that can be directly loaded by the software. We will describe each of them in details in the following sections. All the three tools appear as independent scripts and can be direct run using python command line.

Besides using python command line, this tool also provides a graphic UI (GUI) creadted using [Pyforms](https://github.com/UmSenhorQualquer/pyforms), a wrapper for PyQT4/5. Although the command line tools for `Import` and `Combine` provide path auto-complete function, which makes it easier to choose file or directory using command line, GUI is of course more user friendly. Note that there will be a little difference between CLT and GUI for `Config` tool. Refer to the section below for details.

### Import
This is used to read the *I/O ports* and the *function blocks* of the standardized libraries and export to an **Excel file**. All the external ports and parameteric function blocks should follow standard description form. The input can be a library *file* or a *directory* contains libraries. The output file will be exported to `Library/` directory. This tool will also copy the libraries to this directory.

### Config
This is used to generate Arguments file accroding to **Application plan** from *GUI* or **Config file** from *CLT*.<br>
In *CLT*, it checks whether `Config.xlsx` exists in the current directory. If not, it generates an empty one, otherwise it generates `Arguments.xlsx` according to `Config.xlsx`. User can specifie library, loop name, and start page in the **Config file**.<br>
In *GUI*, user no longer needs to specify `Config.xlsx`, configuration can be directly specified using Application plan in the GUI. Application plan can also be saved and loaded. It is store on disk in `Json` format.

### Combine
This takes a DPU database file and an Argument file, and then generates a new DPU file based on the database and the arguments. The database should contain all the **tags** specified in the Argument file. The Argument file (generated by the config tool) should fill all the tags except the green rows in PARAMETERS, and all the descriptions except the green rows in OUTPUTS and PARAMETERS. Note that this tool needs another file `para_def.txt` to run. This file specifies all the parameters that will set in the Argument file. A sample is provided in the package.

#### Format of `para_def.txt`
This file is plan text (.txt) using UTF-8 encoding. It gives all the parameters that can be changed in the Argument file. The syntax is:
```
Function_Block_Name
P01 #1_parameter_name
P02 #2_parameter_name
...
I01 #1_input_name
I02 #2_input_name
...
Function_Block_Name
...
```
We use `P` to represent parameter and `I` to represent input variable. The number after is the order of the parameter or input variable appears in the parameter or input line in the DPU configuration file, separated by comma. Then, after a space is the parameter or input variable name. Tab also works to separate name and order. Empty line will not affect, but it's better to use empty lines to separate different function blocks to make the file more readable.

## For developers
