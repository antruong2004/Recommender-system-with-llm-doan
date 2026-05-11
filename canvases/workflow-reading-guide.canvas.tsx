import { Card, CardBody, CardHeader, Divider, Grid, H1, H2, Pill, Row, Stack, Stat, Table, Text } from 'cursor/canvas';

const workflows = [
  {
    name: 'request-flow.png',
    purpose: 'Cách request đi từ người dùng → Flask → xử lý → trả response',
    howToRead: [
      'Bắt đầu ở bên trái, đọc theo mũi tên sang phải.',
      'Nếu đi vào ProductManager thì đó là luồng nghiệp vụ / dữ liệu.',
      'Nếu đi vào Vector / Recommender thì đó là luồng gợi ý / tìm kiếm.',
      'Khu vực bên phải là JSON output, trace và debug.',
    ],
    keySignals: ['/api/chat', '/api/recommend', '/api/products'],
  },
  {
    name: 'data-flow.png',
    purpose: 'Mô tả đường đi của dữ liệu và model trong hệ thống',
    howToRead: [
      'Đọc từ các nguồn dữ liệu ở bên trái.',
      'ProductManager là lớp trung gian xử lý và chuẩn hóa.',
      'VectorSearchEngine và AI Recommender là các khối tính toán.',
      'Bên phải là output phục vụ API.',
    ],
    keySignals: ['products.json', 'orders / users', 'product_vectors.json'],
  },
  {
    name: 'api-workflow.png',
    purpose: 'Nhóm các endpoint chính trong routes.py',
    howToRead: [
      'Mỗi box là 1 nhóm endpoint có cùng mục đích.',
      'Đọc theo từng nhóm để biết API nào phục vụ chức năng nào.',
      'Box dưới cùng cho biết dạng trả về có source/trace hay không.',
      'Dùng để map nhanh từ URL sang tính năng.',
    ],
    keySignals: ['/api/health', '/api/products', '/api/recommend', '/api/chat'],
  },
  {
    name: 'chat-flow.png',
    purpose: 'Luồng xử lý hội thoại trong /api/chat',
    howToRead: [
      'Đọc từ input message và session_id ở bên trái.',
      'Nhánh xử lý trending sẽ tách ra nếu có từ khóa phù hợp.',
      'Không trending thì đi vào Advisor.chat() / LLM + retrieval.',
      'Sau cùng lưu history và trả JSON response.',
    ],
    keySignals: ['Trending path', 'Advisor.chat()', 'Save history'],
  },
  {
    name: 'search-flow.png',
    purpose: 'Luồng tìm kiếm, lọc và sắp xếp sản phẩm',
    howToRead: [
      'Bắt đầu từ query params bên trái.',
      'ProductManager.filter_products() là điểm xử lý chính.',
      'Mỗi endpoint con sẽ đưa về một kiểu lọc/trả kết quả khác nhau.',
      'Bên phải là danh sách sản phẩm đã định dạng.',
    ],
    keySignals: ['/api/products/search', '/api/products/top', '/api/products/trending'],
  },
  {
    name: 'health-flow.png',
    purpose: 'Kiểm tra sức khỏe hệ thống',
    howToRead: [
      'Đọc từ client → app.py → routes.py.',
      'Ba khối chính là app, api health, và components.',
      'Kết quả cho biết vector, recommender, db có sẵn sàng không.',
      'Dùng để debug trạng thái tổng thể.',
    ],
    keySignals: ['/api/health', '/api/ai/health', '/api/db/counts'],
  },
  {
    name: 'recommender-flow.png',
    purpose: 'Mô tả cách chọn thuật toán gợi ý',
    howToRead: [
      'Đọc từ input vào bên trái, đó là điều kiện gợi ý.',
      'Khối Hybrid là bộ chọn chiến lược.',
      'Algorithms là tập các phương pháp có thể dùng.',
      'Bên phải là danh sách recommendations đã lọc.',
    ],
    keySignals: ['hybrid', 'popularity', 'tfidf', 'svd', 'cluster'],
  },
  {
    name: 'vector-search-flow.png',
    purpose: 'Tìm kiếm ngữ nghĩa bằng vector',
    howToRead: [
      'Đọc từ search query ở bên trái.',
      'VectorSearchEngine xử lý semantic_search().',
      'Khác với search thường, ở đây cần đo độ tương đồng.',
      'Kết quả bên phải có similarity_score.',
    ],
    keySignals: ['semantic_search()', 'product_vectors.json', 'similarity ranking'],
  },
  {
    name: 'database-flow.png',
    purpose: 'Lưu và đọc dữ liệu từ PostgreSQL',
    howToRead: [
      'Đọc từ API request → DBService → PostgreSQL.',
      'Khu vực này nói về lưu chat, orders, audit logs.',
      'Muốn hiểu luồng này thì nhìn vào read/write arrows.',
      'Bên phải là data đã được lưu trong DB.',
    ],
    keySignals: ['DBService', 'PostgreSQL', 'chat_messages', 'orders'],
  },
  {
    name: 'architecture-overview.png',
    purpose: 'Tổng quan kiến trúc toàn hệ thống',
    howToRead: [
      'Đọc theo cấp: frontend → Flask → routes/core → data/output.',
      'Đây là ảnh để hiểu hệ thống ở mức cao nhất.',
      'Nếu bị rối, hãy quay lại request-flow và data-flow trước.',
      'Dùng để có bức tranh tổng thể trước khi vào chi tiết.',
    ],
    keySignals: ['Frontend', 'Flask App', 'Routes', 'Core', 'DB + Vectors'],
  },
];

function TonePill({ label, tone }: { label: string; tone: 'neutral' | 'success' | 'warning' | 'critical' }) {
  return <Pill tone={tone} size="sm">{label}</Pill>;
}

export default function WorkflowReadingGuideCanvas() {
  return (
    <Stack gap={18}>
      <H1>Cách đọc từng workflow</H1>
      <Text tone="secondary">
        Coi mỗi ảnh như một bản đồ luồng: đọc theo mũi tên, tìm box bên trái là đầu vào,
        box giữa là khối xử lý, và box bên phải là kết quả.
      </Text>

      <Grid columns={4} gap={14}>
        <Stat value="10" label="Workflow đã tạo" tone="success" />
        <Stat value="3" label="Nhóm đọc chính" />
        <Stat value="1" label="Quy tắc đọc" tone="warning" />
        <Stat value="1" label="Điểm bắt đầu" tone="neutral" />
      </Grid>

      <Card>
        <CardHeader title="Quy tắc chung để đọc ảnh" />
        <CardBody>
          <Stack gap={10}>
            <Text>1. Đọc từ trái sang phải, nếu có mũi tên xuống thì là nhánh phụ / fallback.</Text>
            <Text>2. Tiêu đề box cho biết vai trò, subtitle cho biết nó làm gì.</Text>
            <Text>3. Nếu box có tên API, đó thường là endpoint cụ thể.</Text>
            <Text>4. Nếu box có tên model / engine / recommender, đó là lớp xử lý hoặc tính toán.</Text>
            <Text>5. Nếu có JSON / response / trace, đó là đầu ra cuối cùng.</Text>
          </Stack>
        </CardBody>
      </Card>

      <H2>Bảng hướng dẫn đọc từng workflow</H2>
      <Table
        headers={["File", "Mục đích", "Cách đọc nhanh", "Điểm cần chú ý"]}
        rows={workflows.map((item) => [
          item.name,
          item.purpose,
          item.howToRead[0],
          item.keySignals.join(', '),
        ])}
      />

      <H2>Phân tích chi tiết theo nhóm</H2>
      <Grid columns={3} gap={14}>
        <Card>
          <CardHeader title="1. Nhóm request và API" />
          <CardBody>
            <Stack gap={10}>
              <Text weight="medium">Nhóm này: request-flow, api-workflow, health-flow</Text>
              <Text tone="secondary">Cách đọc:</Text>
              <Text>• Xem API nào được gọi.</Text>
              <Text>• Xem nó đi qua Flask App, Routes hay component nào.</Text>
              <Text>• Xem response có trace/source hay không.</Text>
              <Text tone="secondary">Mục tiêu: hiểu đường đi của một HTTP request.</Text>
            </Stack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="2. Nhóm dữ liệu và model" />
          <CardBody>
            <Stack gap={10}>
              <Text weight="medium">Nhóm này: data-flow, database-flow, vector-search-flow</Text>
              <Text tone="secondary">Cách đọc:</Text>
              <Text>• Tìm nguồn dữ liệu ở bên trái.</Text>
              <Text>• Tìm lớp xử lý trung gian ở giữa.</Text>
              <Text>• Tìm output/model ở bên phải.</Text>
              <Text tone="secondary">Mục tiêu: hiểu dữ liệu vào đâu và ra ở đâu.</Text>
            </Stack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="3. Nhóm nghiệp vụ ứng dụng" />
          <CardBody>
            <Stack gap={10}>
              <Text weight="medium">Nhóm này: chat-flow, search-flow, recommender-flow, architecture-overview</Text>
              <Text tone="secondary">Cách đọc:</Text>
              <Text>• Đọc theo use case, không đọc theo code file.</Text>
              <Text>• Dùng để hiểu tính năng người dùng nhìn thấy.</Text>
              <Text>• Architecture-overview là bản đồ tổng thể.</Text>
              <Text tone="secondary">Mục tiêu: nối được tính năng nào dùng luồng nào.</Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <H2>Chú ý riêng cho từng ảnh</H2>
      <Stack gap={12}>
        {workflows.map((item, idx) => {
          const tone = idx % 3 === 0 ? 'success' : idx % 3 === 1 ? 'warning' : 'neutral';
          return (
            <Card key={item.name}>
              <CardHeader
                title={item.name}
                trailing={<TonePill label={idx < 3 ? 'nên đọc đầu tiên' : 'đọc bổ sung'} tone={tone as any} />}
              />
              <CardBody>
                <Stack gap={8}>
                  <Text>{item.purpose}</Text>
                  <Row gap={8} wrap>
                    {item.keySignals.map((signal) => (
                      <Pill key={signal} tone={signal.includes('api') || signal.includes('/') ? 'success' : 'neutral'} size="sm">
                        {signal}
                      </Pill>
                    ))}
                  </Row>
                  <Divider />
                  {item.howToRead.map((step) => (
                    <Text key={step} tone="secondary">• {step}</Text>
                  ))}
                </Stack>
              </CardBody>
            </Card>
          );
        })}
      </Stack>

      <Card>
        <CardHeader title="Thứ tự nên xem nếu muốn hiểu nhanh" />
        <CardBody>
          <Stack gap={8}>
            <Text>1. architecture-overview.png để lấy bản đồ tổng thể.</Text>
            <Text>2. request-flow.png để hiểu đường đi request.</Text>
            <Text>3. data-flow.png và database-flow.png để hiểu dữ liệu.</Text>
            <Text>4. api-workflow.png để map endpoint.</Text>
            <Text>5. chat-flow.png, search-flow.png, recommender-flow.png, vector-search-flow.png để vào từng tính năng.</Text>
          </Stack>
        </CardBody>
      </Card>

      <Text tone="secondary" size="small">
        Nếu bạn muốn, mình có thể làm tiếp một canvas khác: "đọc từng workflow bằng sơ đồ mũi tên và giải thích từng box".
      </Text>
    </Stack>
  );
}
