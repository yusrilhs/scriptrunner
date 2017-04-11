from threading import Thread
from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT
from os import path
from os import chdir
from os import kill
from time import time
from shlex import quote as shell_quote
from shlex import split as shell_split
from signal import SIGINT

import sublime
import sublime_plugin

class RunnerThread(Thread):

    def __init__(self, command, filename, end_callback):
        Thread.__init__(self)
        self.command = command
        self.window = sublime.active_window()
        self.filename = filename
        self.end_callback = end_callback
        self.proc = None
        self.killed = False

    def run(self):
        try:
            self.proc = Popen(
                        shell_split(self.command),
                        universal_newlines=True,
                        stdout=PIPE,
                        stderr=STDOUT,
                        close_fds=True
                   )

            self.window.destroy_output_panel("script_result_panel")
            self.window.create_output_panel("script_result_panel")
            self.window.run_command("stop_run_script", {
                "set_enable": True
            })
            # initialize variable
            line = "File: {0}\n".format(shell_quote(self.filename))

            while line and self.killed is not True:
                self.window.run_command("show_script_result", {
                    "content": line
                })
                self.window.run_command("show_panel", {
                    "panel": "output.script_result_panel"
                })
                line = self.proc.stdout.readline()
            self.end_callback()

        except FileNotFoundError as e:
            sublime.error_message("Error executing: {}. Set environment for the executor.".format(command))
            return False
        # any exception
        except Exception as e:
            self.end_callback()

    def terminate(self):
        if self.proc is not None:
            kill(self.proc.pid, SIGINT)
            self.killed = True


class RunScriptCommand(sublime_plugin.WindowCommand):
    process = None
    can_run = True

    def run(self, kill=False):
        if kill is True:
            self.kill_process()
            return True

        vw = self.window.active_view()
        fullpath = vw.file_name()

        # If the file is not saved
        if fullpath is None:
            sublime.error_message("Save file before run script")
            return False

        dirname, filename = (path.dirname(fullpath), path.basename(fullpath))

        # Read the script runner settings
        settings = sublime.load_settings("scriptrunner.sublime-settings")
        main_file, main_dir = (settings.get('main_file'), settings.get('main_dir'))

        # Change run script into main if specified
        if main_file is not None and main_dir is not None:
            dirname, filename = (main_dir, main_file)

        # Get file extension
        _, extension = path.splitext(filename)

        # Get runner from extension
        runner = settings.get(extension)
        # if runner is not specified
        if runner is None:
            sublime.error_message("Could not find executor for run {0} extension. Please set the command executor on Tools > Run Script Configuration".format(ext))
            return False

        command = runner.format(scriptname=shell_quote(filename))
        # Move directory
        chdir(dirname)

        self.can_run = False
        self.process = RunnerThread(command, filename, self.on_ended)
        self.timestart = time()
        self.process.start()

    def on_ended(self):
        self.window.run_command("stop_run_script", {
            "set_enable": False
        })
        self.window.run_command("show_script_result", {
            "content": "[Finished in {0}]".format(round(time() - self.timestart, 8))
        })
        self.can_run = True

    def is_visible(self):
        return self.can_run is True

    def kill_process(self):
        if self.process is not None:
            self.process.terminate()

class ShowScriptResultCommand(sublime_plugin.TextCommand):
    def run(self, edit, content=''):
        wndw = sublime.active_window()
        pt = wndw.find_output_panel("script_result_panel")
        # Create if panel is not available
        if pt is None:
          pt = wndw.create_output_panel("script_result_panel")

        pt.set_read_only(False)
        pt.insert(edit, pt.size(), content)
        pt.set_read_only(True)
        end_line, _ = pt.rowcol(pt.size())
        tp = pt.text_point(end_line, 0)
        # Move view to the end line
        pt.show(tp)

class StopRunScriptCommand(sublime_plugin.WindowCommand):
    is_enable = False
    def run(self, set_enable=None):
        if set_enable is not None:
            self.is_enable = set_enable
            return True
        wndw = sublime.active_window()
        wndw.run_command("run_script", {"kill": True})

    def is_visible(self):
        return self.is_enable is True
