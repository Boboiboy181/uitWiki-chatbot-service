# LLM Model
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAI
# from langchain_anthropic import AnthropicLLM
# from langchain_huggingface import HuggingFaceEndpoint

from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from app.core.config import settings
from pydantic import SecretStr

api_key = SecretStr(settings.GOOGLE_API_KEY)


def filter_by_metadata(question, new_db):
    metadata_field_info = [
        AttributeInfo(
            name="title",
            description="Tên của tài liệu chứa thông tin cần truy xuất",
            type="string",
        ),
        AttributeInfo(
            name="author",
            description="Phòng ban quản lý tài liệu",
            type="string",
        ),
        AttributeInfo(
            name="description",
            description="Mô tả nội dung của tài liệu",
            type="string",
        ),
        AttributeInfo(
            name="category",
            description="Quy định, chính sách, quy trình, hướng dẫn",
            type="string",
        ),
        AttributeInfo(
            name="tags",
            description="Các từ khóa liên quan đến đoạn văn cần truy xuất",
            type="string"
        ),
        AttributeInfo(
            name="target audience",
            description="Đối tượng cần sử dụng",
            type="string"
        ),
    ]
    document_content_description = "Tóm tắt nội dung của tài liệu trên "
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", temperature=0, api_key=api_key)
    retriever = SelfQueryRetriever.from_llm(
        llm,
        new_db,
        document_content_description,
        metadata_field_info,
        verbose=True,
    )
    docs = retriever.invoke(question)
    return docs


def get_conversational_chain():

    prompt_template = """
    Tên của bạn là UITWikiBot.
    Được phát triển bởi nhóm sinh viên UIT: Hiển Đoàn và Hải Đào dưới sự hướng dẫn của thầy Tín.
    Vai trò của bạn là:
    - Bạn là một trợ lý ảo giải đáp của sinh viên tại trường Đại học Công nghệ Thông tin UIT.
    - Nhiệm vụ của bạn là trả lời các câu hỏi và thắc mắc của sinh viên một cách chi tiết và chính xác nhất.
    - Metadata cũng có thể là chứa keyword mà trong câu hỏi có. Context có thể chính là nơi chứa đáp án của câu hỏi.
    - Hãy trả lời câu hỏi dựa trên các thông tin được cung cấp trong context và metadata.
    - Trong đó, context chính là nơi chứa đáp án của câu hỏi và metadata cũng có thể trả lời một số thông tin quan trọng đi kèm
    - Context là những mẫu bối cảnh rời rạc. Do đó, bạn hãy chắt lọc, ghép nối các context để trả lời câu hỏi một cách hợp lý .
    -------------------------

    Dưới đây là thông tin tôi sẽ đưa bạn :
    *METADATA* là: ({metadata})
    ---
    *CONTEXT* là: ({context})
    ---
    *QUESTION* là: ({question}?)
    -------------------------

    Yêu cầu về câu trả lời:
    - Hãy đảm bảo cung cấp đầy đủ chi tiết theo METADATA,CONTEXT.
    - Cố gắng liên kết thông tin giữa METADATA,CONTEXT để tạo ra câu trả lời chính xác nhất.
    - Hãy sắp xếp câu trả lời thành một cấu trúc đẹp dưới dạng Markdown. Ở những câu trả lời về quy định, các bước thực hiện, hãy sắp xếp câu trả lời theo thứ tự
    Bạn không cần phải trả lời dựa vào đâu (Dựa vào METADATA được cung cấp...., dựa vào CONTEXT ta thấy,...)
    - Đưa ra một câu trả lời tự nhiên và dễ hiểu nhất có thể.
    - Không tự trả lời mà không có trong METADATA,CONTEXT. Nếu không có hãy trả lời (Vui lòng cung cấp thêm thông tin chi tiết)
    - Bạn có thể trích dẫn tên tài liệu chứa thông tin hoặc nội dung đó nằm ở phần nào của tài liệu đó.
    - Với những dạng YES/NO, hãy trả lời rõ ràng và chi tiết nhất có thể, phải giải thích vì sao trả lời như vậy dựa trên trích dẫn thông tin đó lấy từ tài liệu nào
    - Những câu trả lời có đường dẫn đến link URL hay đường dẫn để download, bạn hãy embed link đó vào câu trả lời của mình .
    - Hãy embed đường dẫn tải các mẫu đơn vào tên mẫu đơn đó.
       * Ví dụ như : [Đường dẫn tải mẫu đơn](https://www.uit.edu.vn)
    """

    model = GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0,
                               api_key=api_key)

    prompt = PromptTemplate(template=prompt_template, input_variables=[
                            "context", "question", 'metadata'])
    chain = load_qa_chain(model, chain_type="stuff",
                          prompt=prompt, verbose=True)
    return chain
