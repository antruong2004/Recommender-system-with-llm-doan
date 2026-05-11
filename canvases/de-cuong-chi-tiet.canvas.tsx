import { Card, CardBody, CardHeader, Divider, Grid, H1, H2, H3, Pill, Row, Stack, Stat, Table, Text } from 'cursor/canvas';

const sections = [
  {
    chapter: 'Phần mở đầu',
    purpose: 'Giới thiệu đề tài, lý do, mục tiêu, câu hỏi và phạm vi nghiên cứu',
    items: [
      'Lý do chọn đề tài: nêu vấn đề thực tiễn, tính cấp thiết, bối cảnh công nghệ và nhu cầu người dùng.',
      'Mục tiêu nghiên cứu: mục tiêu tổng quát và mục tiêu cụ thể của khóa luận.',
      'Đối tượng và khách thể: xác định hệ thống, người dùng, dữ liệu, doanh nghiệp.',
      'Phạm vi nghiên cứu: phạm vi nội dung, không gian, thời gian, dữ liệu.',
      'Câu hỏi nghiên cứu: 3–5 câu hỏi bám sát vấn đề chính.',
      'Phương pháp nghiên cứu: định tính, định lượng, phân tích tài liệu, khảo sát, thử nghiệm.',
      'Kết cấu khóa luận: mô tả ngắn gọn bố cục các chương.',
    ],
    keywords: ['lý do', 'mục tiêu', 'phạm vi', 'phương pháp'],
  },
  {
    chapter: 'Chương 1',
    purpose: 'Cơ sở lý thuyết và tổng quan nghiên cứu',
    items: [
      'Giải thích các khái niệm nền tảng: recommender system, semantic search, chatbot, personalization, NLP, AI trong TMĐT.',
      'Tổng quan nghiên cứu trong nước: những hướng nghiên cứu liên quan, ưu điểm, hạn chế.',
      'Tổng quan nghiên cứu quốc tế: mô hình, phương pháp, kết quả nổi bật, xu hướng mới.',
      'Khoảng trống nghiên cứu: chỉ ra điều chưa được giải quyết hoặc chưa phù hợp với bối cảnh đề tài.',
      'Khung lý thuyết: chọn lý thuyết nền tảng để giải thích các biến nghiên cứu.',
      'Mô hình nghiên cứu đề xuất: mô tả các biến, quan hệ giữa chúng, và logic xây dựng.',
      'Giả thuyết nghiên cứu: H1, H2, H3… dựa trên cơ sở lý thuyết và thực tiễn.',
    ],
    keywords: ['khái niệm', 'nghiên cứu trước', 'khoảng trống', 'giả thuyết'],
  },
  {
    chapter: 'Chương 2',
    purpose: 'Giới thiệu doanh nghiệp và thực trạng vấn đề nghiên cứu',
    items: [
      'Giới thiệu doanh nghiệp: lịch sử, lĩnh vực hoạt động, mô hình kinh doanh, sản phẩm/dịch vụ.',
      'Hệ thống hiện tại: mô tả website/app, cách người dùng tìm sản phẩm, cách tư vấn hiện tại.',
      'Thực trạng vấn đề: điểm nghẽn, khó khăn của người dùng, hạn chế về dữ liệu và tư vấn.',
      'Phân tích nhu cầu cải thiện: vì sao cần hệ thống gợi ý, tìm kiếm ngữ nghĩa và chatbot.',
      'Đánh giá sơ bộ: hiện trạng tốt/chưa tốt ở đâu, từ đó dẫn sang chương giải pháp.',
    ],
    keywords: ['doanh nghiệp', 'thực trạng', 'vấn đề', 'nhu cầu'],
  },
  {
    chapter: 'Chương 3',
    purpose: 'Phương pháp nghiên cứu và thiết kế nghiên cứu',
    items: [
      'Thiết kế nghiên cứu: trình bày toàn bộ quy trình từ ý tưởng đến kiểm định.',
      'Quy trình xây dựng bảng hỏi: từ biến nghiên cứu đến câu hỏi khảo sát.',
      'Thang đo nháp: xây dựng ban đầu các biến quan sát.',
      'Nghiên cứu định tính: phỏng vấn chuyên gia, phỏng vấn người dùng, hiệu chỉnh thang đo.',
      'Nghiên cứu định lượng sơ bộ: kiểm tra độ tin cậy, loại biến xấu.',
      'Nghiên cứu định lượng chính thức: lấy mẫu, thu thập dữ liệu, xử lý dữ liệu.',
      'Trình tự phân tích dữ liệu: Cronbach’s Alpha, EFA, kiểm định mô hình đo lường, mô hình cấu trúc.',
    ],
    keywords: ['thiết kế', 'bảng hỏi', 'định tính', 'định lượng'],
  },
  {
    chapter: 'Chương 4',
    purpose: 'Kết quả nghiên cứu và kiểm định',
    items: [
      'Thống kê mô tả: giới tính, độ tuổi, nghề nghiệp, tần suất sử dụng, thói quen mua sắm.',
      'Kiểm định Cronbach’s Alpha: độ tin cậy của từng thang đo.',
      'Phân tích EFA: rút gọn và xác nhận cấu trúc nhân tố.',
      'Đánh giá mô hình đo lường: hội tụ, phân biệt, outer loading.',
      'Kiểm định mô hình cấu trúc: đa cộng tuyến, tác động trực tiếp/gián tiếp.',
      'Kiểm định R², f², giả thuyết nghiên cứu: mức độ giải thích và ý nghĩa thống kê.',
      'Tổng hợp kết quả: chấp nhận hay bác bỏ từng giả thuyết.',
    ],
    keywords: ['Cronbach', 'EFA', 'outer loading', 'R²'],
  },
  {
    chapter: 'Chương 5',
    purpose: 'Thảo luận và đề xuất giải pháp',
    items: [
      'Thảo luận kết quả: ý nghĩa của các phát hiện nghiên cứu.',
      'Đóng góp lý luận: bổ sung cho lý thuyết, mô hình, cách tiếp cận.',
      'Đóng góp thực tiễn: giá trị ứng dụng cho doanh nghiệp, hệ thống, người dùng.',
      'Đề xuất giải pháp: tối ưu dữ liệu, cải tiến thuật toán, tăng cá nhân hóa, cải thiện UX.',
      'Hạn chế nghiên cứu: phạm vi dữ liệu, thời gian, mô hình, mẫu khảo sát.',
      'Hướng nghiên cứu tương lai: mở rộng dữ liệu, thêm mô hình, tăng độ chính xác.',
    ],
    keywords: ['thảo luận', 'đóng góp', 'giải pháp', 'hạn chế'],
  },
];

function SectionCard({ chapter, purpose, items, keywords }: (typeof sections)[number]) {
  return (
    <Card>
      <CardHeader
        title={chapter}
        trailing={
          <Row gap={8} wrap>
            {keywords.map((k) => (
              <Pill key={k} tone="neutral" size="sm">
                {k}
              </Pill>
            ))}
          </Row>
        }
      />
      <CardBody>
        <Stack gap={10}>
          <Text>{purpose}</Text>
          <Divider />
          {items.map((item) => (
            <Text key={item}>• {item}</Text>
          ))}
        </Stack>
      </CardBody>
    </Card>
  );
}

export default function DeCuongChiTietCanvas() {
  return (
    <Stack gap={18}>
      <H1>Chi tiết từng phần của đề cương khóa luận</H1>
      <Text tone="secondary">
        Đây là bản gợi ý triển khai chi tiết theo đúng bố cục bạn đã đưa ra. Mục tiêu là giúp bạn biết
        mỗi phần nên viết gì, nên tìm gì, và nên đào sâu ở đâu.
      </Text>

      <Grid columns={4} gap={14}>
        <Stat value="6" label="Nhóm nội dung lớn" tone="success" />
        <Stat value="32" label="Mục cần viết" />
        <Stat value="1" label="Mô hình nghiên cứu" tone="warning" />
        <Stat value="1" label="Hướng triển khai" tone="neutral" />
      </Grid>

      <Card>
        <CardHeader title="Cách tìm kiếm chi tiết từng phần" />
        <CardBody>
          <Stack gap={8}>
            <Text>1. Với mỗi mục, xác định mục tiêu của mục đó là gì.</Text>
            <Text>2. Tìm 3–5 ý chính cần có trong mục.</Text>
            <Text>3. Với phần lý thuyết, ưu tiên tài liệu học thuật, bài báo, giáo trình và nghiên cứu trước.</Text>
            <Text>4. Với phần thực trạng, ưu tiên dữ liệu thực tế, mô tả hệ thống và vấn đề đang tồn tại.</Text>
            <Text>5. Với phần phương pháp và kết quả, trình bày rõ quy trình, công cụ và cách kiểm định.</Text>
          </Stack>
        </CardBody>
      </Card>

      <H2>Chi tiết theo từng chương</H2>
      <Stack gap={14}>
        {sections.map((section) => (
          <SectionCard key={section.chapter} {...section} />
        ))}
      </Stack>

      <H2>Gợi ý tìm kiếm tài liệu cho từng phần</H2>
      <Table
        headers={["Phần cần tìm", "Từ khóa gợi ý", "Nguồn nên đọc", "Mục đích"]}
        rows={[
          [
            'Lý do chọn đề tài',
            'AI trong thương mại điện tử, cá nhân hóa mua sắm, recommender system',
            'Bài báo tổng quan, báo cáo thị trường, giáo trình',
            'Chứng minh tính cấp thiết',
          ],
          [
            'Tổng quan nghiên cứu',
            'semantic search, chatbot, hybrid recommendation, personalized recommendation',
            'Google Scholar, Scopus, sách chuyên ngành',
            'Xây dựng nền tảng học thuật',
          ],
          [
            'Mô hình nghiên cứu',
            'theoretical framework, conceptual model, hypothesis',
            'Nghiên cứu trước và mô hình lý thuyết',
            'Tạo khung phân tích',
          ],
          [
            'Thực trạng doanh nghiệp',
            'website bán hàng, vấn đề tìm kiếm sản phẩm, hành vi người dùng',
            'Dữ liệu nội bộ, quan sát thực tế',
            'Chỉ ra vấn đề cần giải quyết',
          ],
          [
            'Phương pháp nghiên cứu',
            'qualitative research, quantitative research, survey, EFA, Cronbach',
            'Giáo trình phương pháp nghiên cứu',
            'Xác định cách làm bài',
          ],
          [
            'Kết quả và thảo luận',
            'r-squared, effect size, hypothesis testing',
            'Tài liệu thống kê và mô hình PLS-SEM',
            'Diễn giải kết quả nghiên cứu',
          ],
        ]}
      />

      <Grid columns={3} gap={14}>
        <Card>
          <CardHeader title="Bạn nên viết trước" />
          <CardBody>
            <Stack gap={8}>
              <Text>• Phần mở đầu</Text>
              <Text>• Chương 1: cơ sở lý thuyết</Text>
              <Text>• Chương 2: thực trạng</Text>
              <Text>• Khung lý thuyết và mô hình nghiên cứu</Text>
            </Stack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Bạn nên để sau" />
          <CardBody>
            <Stack gap={8}>
              <Text>• Chương 4: kết quả nghiên cứu</Text>
              <Text>• Chương 5: thảo luận và giải pháp</Text>
              <Text>• Kết luận và phụ lục</Text>
            </Stack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Mẹo làm nhanh" />
          <CardBody>
            <Stack gap={8}>
              <Text>• Viết dàn ý trước, sau đó mới mở rộng thành đoạn văn.</Text>
              <Text>• Mỗi mục nên có 2–4 ý chính.</Text>
              <Text>• Phần nào có số liệu thì để số liệu trước khi viết giải thích.</Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Card>
        <CardHeader title="Nếu bạn muốn làm tiếp" />
        <CardBody>
          <Stack gap={8}>
            <Text>Tôi có thể tách tiếp thành từng file riêng cho bạn, ví dụ:</Text>
            <Text>• File 1: Phần mở đầu viết hoàn chỉnh</Text>
            <Text>• File 2: Chương 1 viết hoàn chỉnh</Text>
            <Text>• File 3: Chương 2–5 viết hoàn chỉnh</Text>
            <Text>• File 4: Danh mục từ viết tắt, bảng biểu, tài liệu tham khảo</Text>
          </Stack>
        </CardBody>
      </Card>
    </Stack>
  );
}
