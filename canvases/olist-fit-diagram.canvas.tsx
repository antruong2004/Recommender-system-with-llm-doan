import { Card, CardBody, CardHeader, Divider, Grid, H1, H2, Pill, Row, Stack, Text } from 'cursor/canvas';

function Box({ title, items, tone = 'neutral' as const }: { title: string; items: string[]; tone?: 'neutral' | 'success' | 'warning' }) {
  return (
    <Card>
      <CardHeader title={title} trailing={<Pill tone={tone}>{tone === 'success' ? 'phu hop' : tone === 'warning' ? 'can bo sung' : 'binh thuong'}</Pill>} />
      <CardBody>
        <Stack gap={8}>
          {items.map((item) => (
            <Text key={item}>• {item}</Text>
          ))}
        </Stack>
      </CardBody>
    </Card>
  );
}

export default function OlistFitDiagramCanvas() {
  return (
    <Stack gap={18}>
      <H1>Bộ dữ liệu Olist phù hợp như thế nào?</H1>
      <Text tone="secondary">
        Sơ đồ này cho thấy Olist nên dùng cho phần nào trong khóa luận / project, và phần nào nên giữ bằng dữ liệu riêng của TechStore AI.
      </Text>

      <Grid columns={2} gap={14}>
        <Card>
          <CardHeader title="Olist dataset" />
          <CardBody>
            <Stack gap={10}>
              <Text>• Dữ liệu thương mại điện tử chuẩn hóa</Text>
              <Text>• Có khách hàng, đơn hàng, sản phẩm, review, thanh toán</Text>
              <Text>• Phù hợp để phân tích hành vi mua và xây dựng recommender</Text>
              <Text>• Dùng tốt cho thống kê, dashboard, trending, analytics</Text>
            </Stack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="TechStore AI dataset" />
          <CardBody>
            <Stack gap={10}>
              <Text>• Dữ liệu sản phẩm theo bối cảnh shop công nghệ</Text>
              <Text>• Phù hợp cho chatbot tiếng Việt và semantic search</Text>
              <Text>• Dễ mô phỏng câu hỏi người dùng thực tế</Text>
              <Text>• Nên giữ riêng để demo luồng tư vấn</Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Divider />

      <H2>Sơ đồ gợi ý cách dùng</H2>
      <Grid columns={3} gap={14}>
        <Box
          title="Phần nên dùng Olist"
          tone="success"
          items={[
            'Phân tích đơn hàng',
            'Thống kê khách hàng',
            'Gợi ý sản phẩm theo lịch sử mua',
            'Tính trending / popularity',
          ]}
        />
        <Box
          title="Phần nên dùng dữ liệu riêng"
          tone="warning"
          items={[
            'Chatbot tư vấn',
            'Semantic search tiếng Việt',
            'Tên sản phẩm TechStore',
            'Workflow app.py / routes.py',
          ]}
        />
        <Box
          title="Phần nên kết hợp cả hai"
          tone="neutral"
          items={[
            'Mô hình recommender',
            'Báo cáo kết quả nghiên cứu',
            'So sánh hiệu quả',
            'Minh họa tính ứng dụng thực tế',
          ]}
        />
      </Grid>

      <Divider />

      <H2>Sơ đồ luồng sử dụng</H2>
      <Card>
        <CardBody>
          <Stack gap={14}>
            <Row gap={10} wrap>
              <Pill tone="success">Olist</Pill>
              <Text>→ dữ liệu giao dịch / hành vi mua</Text>
            </Row>
            <Row gap={10} wrap>
              <Pill tone="success">Olist</Pill>
              <Text>→ phân tích thống kê / báo cáo / trending</Text>
            </Row>
            <Row gap={10} wrap>
              <Pill tone="warning">TechStore AI</Pill>
              <Text>→ chatbot / tìm kiếm ngữ nghĩa / demo sản phẩm</Text>
            </Row>
            <Row gap={10} wrap>
              <Pill tone="neutral">Kết hợp</Pill>
              <Text>→ khóa luận vừa có dữ liệu thật kiểu e-commerce, vừa có trải nghiệm tư vấn riêng</Text>
            </Row>
          </Stack>
        </CardBody>
      </Card>

      <Divider />

      <H2>Kết luận ngắn</H2>
      <Card>
        <CardBody>
          <Stack gap={8}>
            <Text>• Olist phù hợp cho phần dữ liệu giao dịch và phân tích thương mại điện tử.</Text>
            <Text>• TechStore AI phù hợp cho phần hội thoại, tìm kiếm và mô phỏng tư vấn tiếng Việt.</Text>
            <Text>• Cách tốt nhất là dùng Olist cho nền dữ liệu, còn logic chat và semantic search để riêng.</Text>
          </Stack>
        </CardBody>
      </Card>
    </Stack>
  );
}
