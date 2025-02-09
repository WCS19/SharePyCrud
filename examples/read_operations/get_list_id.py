from sharepycrud.clientFactory import ClientFactory
from sharepycrud.config import SharePointConfig
from sharepycrud.logger import setup_logging, get_logger

logger = get_logger("main.errors")


def main() -> None:
    setup_logging(level="INFO", log_file="get_list_id.log", use_colors=False)
    config = SharePointConfig.from_env()
    read_client = ClientFactory.create_read_client(config)

    site_id = read_client.get_site_id(site_name="TestSite1")
    if not site_id:
        return

    all_lists = read_client.list_lists(site_id=site_id)
    if not all_lists:
        return

    list_id = read_client.get_list_id_by_name(site_id=site_id, list_name="TestList1")
    if not list_id:
        return


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
