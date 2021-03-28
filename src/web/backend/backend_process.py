from collections import OrderedDict


def paginate(stock_list, page_per_size):
    """
    1. split stock_list into dict with key of number
    2. Each number of key represent page number
    Args:
        stock_list (list): stock list
        page_per_size (int): size of stock list per page

    Returns:
        dict with a key of page number
    """
    stock_page = OrderedDict()
    if len(stock_list) <= page_per_size:
        stock_page[1] = stock_list
        return stock_page
    for page in range(1,len(stock_list)//page_per_size+1):
        stock_page[page] = stock_list[(page-1)*page_per_size: page_per_size*page]
    else:
        stock_page[page+1] = stock_list[(page)*page_per_size:]
    return stock_page


if __name__ == '__main__':
    from src.build_data.Conversion import GenerateDB
    from src.database.table import Company

    with GenerateDB() as session:
        stock_list = session.query(Company).all()
    print(stock_list)