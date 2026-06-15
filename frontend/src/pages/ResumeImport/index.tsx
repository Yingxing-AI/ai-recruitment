import { InboxOutlined } from '@ant-design/icons';
import { Button, Form, InputNumber, Typography, Upload } from 'antd';

export default function ResumeImport() {
  return (
    <>
      <div className="page-header">
        <Typography.Title level={3}>简历导入</Typography.Title>
      </div>
      <div className="panel">
        <Form layout="vertical" style={{ maxWidth: 720 }}>
          <Form.Item label="候选人 ID" name="candidate_id" required>
            <InputNumber min={1} style={{ width: 240 }} />
          </Form.Item>
          <Form.Item label="上传简历">
            <Upload.Dragger name="file" multiple={false} beforeUpload={() => false}>
              <p className="ant-upload-drag-icon"><InboxOutlined /></p>
              <p className="ant-upload-text">拖拽 PDF / DOCX 简历到此处，或点击选择文件</p>
            </Upload.Dragger>
          </Form.Item>
          <Button type="primary">开始导入</Button>
        </Form>
      </div>
    </>
  );
}
