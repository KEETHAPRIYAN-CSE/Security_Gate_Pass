-- Update visitors table for BLOB photo storage
-- Run this script in phpMyAdmin to update the existing visitors table

-- Drop the old photo_path column
ALTER TABLE visitors DROP COLUMN photo_path;

-- Add new BLOB photo storage columns
ALTER TABLE visitors 
ADD COLUMN photo_data LONGBLOB COMMENT 'Binary photo data',
ADD COLUMN photo_mime_type VARCHAR(100) COMMENT 'Photo content type (image/jpeg, etc)';

-- Display success message
SELECT 'Photo storage migration complete! Now using BLOB storage.' AS Status;

-- Check table structure
DESCRIBE visitors;