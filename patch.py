import pkgutil
import zipimport
pkgutil.ImpImporter = zipimport.zipimporter
