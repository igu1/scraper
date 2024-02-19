from icrawler.builtin import GoogleImageCrawler


def create_image(image, amount):
    google_crawler = GoogleImageCrawler(storage={"root_dir": f"img/{image}"})
    google_crawler.crawl(
        keyword=image,
        max_num=amount,
        overwrite=True,
    )
