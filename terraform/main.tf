provider "aws" {
  region = "us-east-1"
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "safesync_backup" {
  bucket = "safesync-backup-${random_id.suffix.hex}"
  force_destroy = true
}

resource "aws_iam_user" "safesync_user" {
  name = "safesync-user"
}

resource "aws_iam_access_key" "safesync_keys" {
  user = aws_iam_user.safesync_user.name
}

resource "aws_iam_user_policy" "safesync_policy" {
  name = "safesync-s3-policy"
  user = aws_iam_user.safesync_user.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource = [
          "${aws_s3_bucket.safesync_backup.arn}",
          "${aws_s3_bucket.safesync_backup.arn}/*"
        ]
      }
    ]
  })
}

output "bucket_name" {
  value = aws_s3_bucket.safesync_backup.bucket
}

output "aws_access_key_id" {
  value = aws_iam_access_key.safesync_keys.id
}

output "aws_secret_access_key" {
  value = aws_iam_access_key.safesync_keys.secret
  sensitive = true
}
