# LibMaster
LibMaster is a tool that enables repeatedly using similar function blocks in different DPU configration files. It takes **DPU libraries** and a **DPU database**, and then generates a new DPU file following an **Application plan**. Before using this tool, users should have DPU libraries with **correct standards**, which will be specified in this README.

To get the lastest update of this tool, please refer to [source code](https://github.com/jiyao94/LibMaster) on GitHub.

## Installation
To run this tool, first download or clone `source code` from GitHub. Then you need to install `Python 3.x` for whatever version or platform you use. The tool has been developed and tested under Python 3.6 32 and 64 bits for Windows, and also Python 3.5 for Linux.

### Packaging stand alone execution file for Windows


## Library Standards


## Tool Instructions
This tool is consisted of three parts in order. `Import` reads standardized libraries and generates a list of inputs, outputs, and function blocks that can be parameterized. `Config` generates an **Argument file** for user to specify connections and parameters for each library accorading to the Application plan. `Combine` takes the database** and Argument file and outputs the new DPU file that can be directly loaded by the software. We will describe each of them in details in the following sections. All the three tools appear as independent scripts and can be direct run using python command line.

Besides using python command line, this tool also provides a UI creadted using [Pyforms](https://github.com/UmSenhorQualquer/pyforms), a wrapper for PyQT4/5. Although the command line tools for `Import` and `Combine` provide path auto-complete function, which makes it easier to choose file or directory using command line, UI is of course more user friendly. Note that there will be a little difference between CLT and UI for `Config` tool. Refer to the section below for details.

### Import
This is used to read the *I/O ports* and the *function blocks* of the standardized libraries and export to an **Excel file**. All the external ports and parameteric function blocks should follow standard description form. The input can be a library *file* or a *directory* contains libraries. The output file will be exported to `./Library` directory. This tool will also copy the libraries to this directory.

### Config
This is used to generate Arguments file accroding to **Application plan** from *UI* or **Config file** from *CLT*.<br>
In *CLT*, it checks whether `Config.xlsx` exists in the current directory. If not, it generates an empty one, otherwise it generates `Arguments.xlsx` according to `Config.xlsx`. User can specifie library, loop name, and start page in the **Config file**.<br>
In *UI*, user no longer needs to specify `Config.xlsx`, configuration can be directly specified using Application plan in the UI. Application plan can also be saved and loaded. It is store on disk in `Json` format.

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
We use `P` to represent parameter and `I` to represent input variable. The number after is the order of the parameter or input variable appears in the parameter or input line in the DPU configration file, separated by comma. Then, after a space is the parameter or input variable name. Tab also works to separate name and order. Empty line will not affect, but it's better to use empty lines to separate different function blocks to make the file more readable.

## For developers
