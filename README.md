# img_org
Trivially reorganizes and renames image (JPEG) and some video (AVI, MOV) files based on chronology from metadata

## Usage
```Usage: img_org.py [OPTIONS]

Options:
  -s, --source TEXT       Source path  [required]
  -d, --destination TEXT  Destination path  [required]
  -y, --yearly            Organize into yearly subfolders
  -m, --monthly           Organize into monthly subfolders (implies yearly)
```

### External requirements
Phil Harvey's excellent [ExifTool](https://www.sno.phy.queensu.ca/~phil/exiftool/)
