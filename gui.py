import wx
import subprocess
import threading
import re
import os
import sys

class MyFrame2(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Gutenberg2epub", pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.panel = wx.Panel(self)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText1 = wx.StaticText(self.panel, wx.ID_ANY, u"Gutenberg2Epub", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer1.Add(self.m_staticText1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.m_textCtrl1 = wx.TextCtrl(self.panel, wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TE_PROCESS_ENTER)
        self.m_textCtrl1.SetHint(u"URL Eingeben")  # Set the placeholder text
        bSizer1.Add(self.m_textCtrl1, 0, wx.ALL | wx.EXPAND, 5)

        current_directory = os.path.join(os.getcwd(), "output")  # Get the current directory
        self.output_dir_picker = wx.DirPickerCtrl(self.panel, wx.ID_ANY, path=current_directory, style=wx.DIRP_DEFAULT_STYLE | wx.DIRP_USE_TEXTCTRL)
        bSizer1.Add(self.output_dir_picker, 0, wx.ALL | wx.EXPAND, 5)



        self.m_button1 = wx.Button(self.panel, wx.ID_ANY, u"Buch laden", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer1.Add(self.m_button1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.panel.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

        # Bind the button click event to a method
        self.m_button1.Bind(wx.EVT_BUTTON, self.on_load_book_button)

    def on_load_book_button(self, event):
        self.m_button1.Disable()
        url = self.m_textCtrl1.GetValue()
        output_directory = self.output_dir_picker.GetPath()  # Get the selected output directory

        # Validate the URL pattern
        valid_url_pattern = r'https://www\.projekt-gutenberg\.org/.+/.+/'
        if not re.match(valid_url_pattern, url):
            wx.MessageBox("Ungültiges URL-Format! Bitte geben Sie eine gültige Gutenberg-de-URL ein.", "Error")
            self.m_button1.Enable()
            return


        # Run the scraping process using a thread
        scraping_thread = threading.Thread(target=self.run_scraping, args=(url, output_directory))
        scraping_thread.start()

    def run_scraping(self, url, output_directory):
        import os
        import sys

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
            result = subprocess.run([gscraper_script_path, url], capture_output=True, text=True)
        elif exe == False:      
           result = subprocess.run(["python", "optimized_Scraper.py", url, "-d", output_directory], capture_output=True, text=True)

        output_directory = result.stdout.strip()

        # Run the ebook conversion process using a thread
        conversion_thread = threading.Thread(target=self.run_conversion, args=(output_directory,))
        conversion_thread.start()

    def run_conversion(self, output_directory):

        if getattr(sys, 'frozen', False):
            # Running as executable
            bundle_dir = sys._MEIPASS
            exe = True
        else:
            # Running as script
            bundle_dir = os.path.dirname(os.path.abspath(__file__))
            exe = False

        if exe == True:
            test_script_path = os.path.join(bundle_dir, "test.exe")
            subprocess.run([test_script_path, output_directory])

        elif exe == False:      
            test_script_path = os.path.join(bundle_dir, "test.py")
            subprocess.run(["python", test_script_path, output_directory])




        # Show a message when the conversion is complete
        wx.CallAfter(self.show_conversion_complete_message)

    def show_conversion_complete_message(self):
        self.m_button1.Enable()
        wx.MessageBox("Ebook conversion complete!", "Info")

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame2(None)
    frame.Show(True)
    app.MainLoop()
