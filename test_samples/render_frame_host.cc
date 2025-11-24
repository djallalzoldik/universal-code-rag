// Sample C++ file for testing
#include <string>
#include <memory>

namespace chrome {
namespace content {

class RenderFrameHost {
 public:
  explicit RenderFrameHost(int id);
  ~RenderFrameHost();
  
  // Sends a message to the renderer
  void SendMessage(const std::string& message);
  
  // Gets the frame ID
  int GetFrameId() const { return frame_id_; }
  
 private:
  int frame_id_;
  std::unique_ptr<std::string> data_;
};

RenderFrameHost::RenderFrameHost(int id) : frame_id_(id) {
  data_ = std::make_unique<std::string>("initialized");
}

RenderFrameHost::~RenderFrameHost() {
  // Cleanup
}

void RenderFrameHost::SendMessage(const std::string& message) {
  // Send IPC message
  if (message.empty()) {
    return;
  }
  // Implementation here
}

}  // namespace content
}  // namespace chrome
