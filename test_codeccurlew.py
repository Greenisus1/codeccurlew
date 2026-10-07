import os,subprocess,sys,tempfile,unittest
from pathlib import Path
import codeccurlew as c
class CodecTests(unittest.TestCase):
    def test_utf8(self):r=c.inspect('é'.encode());self.assertTrue(r['decoded']);self.assertEqual(r['non_ascii_characters'],1)
    def test_bad_utf8(self):self.assertFalse(c.inspect(b'\xff')['decoded'])
    def test_empty(self):self.assertEqual(c.inspect(b'')['characters'],0)
    def test_utf8_bom(self):r=c.inspect(b'\xef\xbb\xbfhello');self.assertEqual(r['bom'],'UTF-8');self.assertEqual(r['characters'],5)
    def test_utf16(self):r=c.inspect('hi'.encode('utf-16'));self.assertTrue(r['decoded']);self.assertEqual(r['characters'],2)
    def test_utf32_before_utf16(self):r=c.inspect(b'\xff\xfe\x00\x00h\x00\x00\x00');self.assertEqual(r['bom'],'UTF-32 LE');self.assertEqual(r['characters'],1)
    def test_explicit(self):r=c.inspect(b'\xff','latin-1');self.assertTrue(r['decoded']);self.assertEqual(r['selection'],'explicit')
    def test_mixed_newlines(self):r=c.inspect(b'a\r\nb\nc\r');self.assertEqual((r['crlf'],r['bare_lf'],r['bare_cr']),(1,1,1));self.assertTrue(r['mixed_cr_lf_styles'])
    def test_nuls(self):r=c.inspect(b'a\x00');self.assertEqual(r['nul_bytes'],1);self.assertEqual(r['nul_characters'],1)
    def test_unicode_separators(self):r=c.inspect('a\u2028b'.encode());self.assertEqual(r['unicode_line_separators'],1);self.assertEqual(r['bare_lf'],0)
    def test_utf16_without_bom_needs_choice(self):self.assertFalse(c.inspect(b'h\x00','utf-16')['decoded']);self.assertTrue(c.inspect(b'h\x00','utf-16-le')['decoded'])
    def test_invalid_encoding(self):
        with self.assertRaises(ValueError):c.inspect(b'a','guess')
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'file';p.write_text('safe')
            with self.assertRaises(FileExistsError):c.save({},p)
    def test_fifo(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fifo';os.mkfifo(p)
            with self.assertRaises(ValueError):c.read(p)
    def test_source_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'file';p.write_bytes(b'a\r\n');c.inspect(c.read(p));self.assertEqual(p.read_bytes(),b'a\r\n')
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'file';p.write_bytes(b'\xff');r=subprocess.run([sys.executable,'codeccurlew.py',str(p)],capture_output=True,text=True);self.assertEqual(r.returncode,1)
if __name__=='__main__':unittest.main()
