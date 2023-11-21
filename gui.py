import requests
import wx
import subprocess
import threading
import re
import os
import sys

def show_error_message(error_message, title="Fehler"):
    wx.MessageBox(f"{title}: {error_message}", title, wx.OK | wx.ICON_ERROR)


class MyFrame2(wx.Frame):
    
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Gutenberg2epub", pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText1 = wx.StaticText(self.panel, wx.ID_ANY, u"Gutenberg2Epub", wx.DefaultPosition, wx.DefaultSize, 0)
        mainSizer.Add(self.m_staticText1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.m_textCtrl1 = wx.TextCtrl(self.panel, wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TE_PROCESS_ENTER)
        self.m_textCtrl1.SetHint(u"URL Eingeben")  # Set the placeholder text
        mainSizer.Add(self.m_textCtrl1, 0, wx.ALL | wx.EXPAND, 5)

        current_directory = os.path.join(os.getcwd(), "output")
        self.output_dir_picker = wx.DirPickerCtrl(self.panel, wx.ID_ANY, path=current_directory, style=wx.DIRP_DEFAULT_STYLE | wx.DIRP_USE_TEXTCTRL)
        mainSizer.Add(self.output_dir_picker, 0, wx.ALL | wx.EXPAND, 5)

        # Create a horizontal box sizer for the "Titelbild hinzufügen" and "Buch laden" buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.add_cover_button = wx.Button(self.panel, wx.ID_ANY, u"Titelbild hinzufügen", wx.DefaultPosition, wx.DefaultSize, 0)
        buttonSizer.Add(self.add_cover_button, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_button1 = wx.Button(self.panel, wx.ID_ANY, u"Buch laden", wx.DefaultPosition, wx.DefaultSize, 0)
        buttonSizer.Add(self.m_button1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Create the collapsible pane for "Advanced Options"
        collpane = wx.CollapsiblePane(self.panel, wx.ID_ANY, "Erweiterte Optionnen:")
        mainSizer.Add(collpane, 0, wx.EXPAND | wx.ALL, 5)

        win = collpane.GetPane()
        paneSz = wx.StaticBoxSizer(wx.VERTICAL, win, "Erweiterte Optionnen:")
        self.include_cover_checkbox = wx.CheckBox(win, wx.ID_ANY, u"Titelbild von der Titelseite entfernen", wx.DefaultPosition, wx.DefaultSize, 0)
        paneSz.Add(self.include_cover_checkbox, 0, wx.ALL | wx.EXPAND, 2)
        self.include_css_checkbox = wx.CheckBox(win, wx.ID_ANY, u"CSS Einbinden", wx.DefaultPosition, wx.DefaultSize, 0)
        self.include_css_checkbox.SetValue(True)
        paneSz.Add(self.include_css_checkbox, 0, wx.ALL | wx.EXPAND, 2)
        self.process_footnotes = wx.CheckBox(win, wx.ID_ANY, u"Popup Fußnoten", wx.DefaultPosition, wx.DefaultSize, 0)
        self.process_footnotes.SetValue(True)
        paneSz.Add(self.process_footnotes, 0, wx.ALL | wx.EXPAND, 2)



        win.SetSizer(paneSz)
        paneSz.SetSizeHints(win)

        self.panel.SetSizer(mainSizer)
        self.Layout()

        self.Centre(wx.BOTH)

        # Bind the button click event to a method
        self.m_button1.Bind(wx.EVT_BUTTON, self.on_load_book_button)
        self.add_cover_button.Bind(wx.EVT_BUTTON, self.on_add_cover_button)
        self.cover_image_path = None
        



    def on_load_book_button(self, event):
        self.m_button1.Disable()
        self.add_cover_button.Disable()
        url_or_path = self.m_textCtrl1.GetValue()
        output_directory = self.output_dir_picker.GetPath()  # Get the selected output directory
        
        if re.match(r'https?://', url_or_path):
        #Check Internet Connection
            try:
                response = requests.get("https://www.projekt-gutenberg.org", timeout=5)
                response.raise_for_status()  # Raise an exception for HTTP errors
            except requests.exceptions.RequestException as e:
                show_error_message("Keine Internetverbindung! Bitte stellen Sie sicher, dass Sie mit dem Internet verbunden sind.", "Error")
                self.m_button1.Enable()
                self.add_cover_button.Enable()
                return
            
            # Validate the URL pattern
            valid_url_pattern = r'https://www\.projekt-gutenberg\.org/.+/.+/'
            if not re.match(valid_url_pattern, url_or_path):
                show_error_message("Ungültiges URL-Format! Bitte geben Sie eine gültige Gutenberg-de-URL ein.", "Error")
                self.m_button1.Enable()
                self.add_cover_button.Enable()
                return

             # Run the scraping process using a thread
            scraping_thread = threading.Thread(target=self.run_scraping, args=(url_or_path, output_directory))
            scraping_thread.start()
        else:
            # The input is a local path, so run localprocess.py
            processing_thread = threading.Thread(target=self.run_local_process, args=(url_or_path, output_directory))
            processing_thread.start()

    def on_add_cover_button(self, event):
        openFileDialog = wx.FileDialog(self, "Choose a cover image", "", "", "Image files (*.jpg;*.png)|*.jpg;*.png", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return

        self.cover_image_path = openFileDialog.GetPath()


    def run_scraping(self, url, output_directory):
        try:

            if getattr(sys, 'frozen', False):
                # Running as executable
                bundle_dir = sys._MEIPASS
                exe = True
            else:
                # Running as script
                bundle_dir = os.path.dirname(os.path.abspath(__file__))
                exe = False

            gscraper_script_path = os.path.join(bundle_dir, "gscraper.exe")

            if exe == True:
                result = subprocess.run([gscraper_script_path, url, "-d", output_directory], capture_output=True, text=True)
            elif exe == False:      
                result = subprocess.run(["python", "gscraper.py", url, "-d", output_directory], capture_output=True, text=True)

            output_directory = result.stdout.strip()
            print(output_directory)
            # Check if the scraping process was successful
            if result.returncode == 0:
                # Run the ebook conversion process using a thread
                conversion_thread = threading.Thread(target=self.run_conversion, args=(output_directory,))
                conversion_thread.start()
            else:
                wx.CallAfter(show_error_message, f"Scraping the book failed: {result.stderr}", "Error")
                self.m_button1.Enable()
                self.add_cover_button.Enable()

        except Exception as e:
            wx.CallAfter(show_error_message, f"An error occurred while scraping the book: {e}", "Error")
            self.m_button1.Enable()
            self.add_cover_button.Enable()

    def run_local_process(self, local_path, output_directory):
        try:

            if getattr(sys, 'frozen', False):
                # Running as executable
                bundle_dir = sys._MEIPASS
                exe = True
            else:
                # Running as script
                bundle_dir = os.path.dirname(os.path.abspath(__file__))
                exe = False

            gscraper_script_path = os.path.join(bundle_dir, "localprocess.exe")

            if exe == True:
                result = subprocess.run([gscraper_script_path, local_path, "-d", output_directory], capture_output=True, text=True)
            elif exe == False:      
                result = subprocess.run(["python", "localprocess.py", local_path, "-d", output_directory], capture_output=True, text=True)

            output_directory = result.stdout.strip()
            print(output_directory)
            # Check if the scraping process was successful
            if result.returncode == 0:
                # Run the ebook conversion process using a thread
                conversion_thread = threading.Thread(target=self.run_conversion, args=(output_directory,))
                conversion_thread.start()
            else:
                wx.CallAfter(show_error_message, f"Scraping the book failed: {result.stderr}", "Error")
                self.m_button1.Enable()
                self.add_cover_button.Enable()

        except Exception as e:
            wx.CallAfter(show_error_message, f"An error occurred while processing the book: {e}", "Error")
            self.m_button1.Enable()
            self.add_cover_button.Enable()


    def run_conversion(self, output_directory):
        try:
            if getattr(sys, 'frozen', False):
                # Running as executable
                bundle_dir = sys._MEIPASS
                exe = True
            else:
                # Running as script
                bundle_dir = os.path.dirname(os.path.abspath(__file__))
                exe = False

            if exe == True:
                test_script_path = os.path.join(bundle_dir, "converter.exe")
                if self.cover_image_path:
                    subprocess.run([test_script_path, "-d", output_directory, "--addcover", self.cover_image_path,"--deletedecover", str(self.include_cover_checkbox.GetValue()), "--remove-css", str(not self.include_css_checkbox.GetValue()), "--popup-footnotes", str(self.process_footnotes.GetValue())])
                else:
                    subprocess.run([test_script_path, "-d", output_directory,"--deletedecover", str(self.include_cover_checkbox.GetValue()), "--remove-css", str(not self.include_css_checkbox.GetValue()), "--popup-footnotes", str(self.process_footnotes.GetValue())])

            elif exe == False:      
                test_script_path = os.path.join(bundle_dir, "converter.py")
                if self.cover_image_path:
                    subprocess.run(["python", test_script_path, "-d", output_directory, "--addcover", self.cover_image_path, "--deletedecover", str(self.include_cover_checkbox.GetValue()), "--remove-css", str(not self.include_css_checkbox.GetValue()), "--popup-footnotes", str(self.process_footnotes.GetValue())])
                else:
                    subprocess.run(["python", test_script_path, "-d", output_directory,"--deletedecover", str(self.include_cover_checkbox.GetValue()), "--remove-css", str(not self.include_css_checkbox.GetValue()), "--popup-footnotes", str(self.process_footnotes.GetValue())])
            
            wx.CallAfter(self.show_conversion_complete_message)
        
        except Exception as e:
            wx.CallAfter(show_error_message, f"An error occurred while converting the book: {e}", "Error")


    def show_conversion_complete_message(self):
        self.m_button1.Enable()
        self.add_cover_button.Enable()
        wx.MessageBox("Ebook conversion complete!", "Info")


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame2(None)
    frame.Show(True)
    app.MainLoop()
