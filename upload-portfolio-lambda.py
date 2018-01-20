import boto3
import zipfile
from io import BytesIO
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:127458414699:DepoloyPortfolioTopic')

    try:
        s3 = boto3.resource('s3')

        portfolio_bucket = s3.Bucket('portfolio.juhafagerstedt.com')
        build_bucket = s3.Bucket('portfolio.juhafagerstedt.com.build')

        portfolio_zip = BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print "Job done!"
        topic.publish(Subject="Portfolio deployed", Message="Portfolio depolyment successfull")
    except:
        topic.publish(Subject="Portfolio deployment failed", Message="The portfolio was not deployed succesfully")
        raise

    return 'Hello from Lambda'
