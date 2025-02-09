# from sharepycrud.clientFactory import ClientFactory
# from sharepycrud.config import SharePointConfig
# from sharepycrud.logger import setup_logging, get_logger

# logger = get_logger("delete_list")


# def main():
#     setup_logging(level="INFO", log_file="delete_list.log", use_colors=False)
#     config = SharePointConfig.from_env()
#     read_client = ClientFactory.create_read_client(config)
#     delete_client = ClientFactory.create_delete_client(config)

#     site_id = read_client.get_site_id(site_name="TestSite1")
#     logger.info(f"Site ID: {site_id}")
#     if not site_id:
#         logger.error("Failed to get site ID")
#         return

#     list_id = read_client.get_list_id(site_id=site_id, list_name="TestList1")
#     logger.info(f"List ID: {list_id}")
#     if not list_id:
#         logger.error("Failed to get list ID")
#         return

#     delete_success = delete_client.delete_list_by_id(site_id=site_id, list_id=list_id)
#     if not delete_success:
#         logger.info("Failed to delete list")
#         return
#     else:
#         logger.info("List deleted successfully")


# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         logger.error(f"An error occurred: {e}")
