import React, { useEffect, useRef } from 'react';

const WebChatComponent = () => {
  const webchatRef = useRef(null);

  useEffect(() => {
    // 检查 WebChat 是否已经加载
    if (!window.WebChat) {
      const script = document.createElement('script');
      script.src = 'https://cdn.botframework.com/botframework-webchat/latest/webchat.js';
      script.async = true;
      script.onload = () => {
        console.log('BotFramework WebChat script loaded.');
        initializeWebChat(); // 当脚本加载完成后初始化 WebChat
      };
      document.body.appendChild(script);
    } else {
      initializeWebChat(); // 如果 WebChat 已加载，直接初始化
    }

    function initializeWebChat() {
      if (window.WebChat && webchatRef.current) {
        const directLine = window.WebChat.createDirectLine({
          token: "YOUR_DIRECT_LINE_SECRET"
        });

        window.WebChat.renderWebChat(
          { directLine },
          webchatRef.current
        );
      }
    }
  }, []);

  return <div ref={webchatRef} style={{ width: '100%', height: '500px' }} />;
};

export default WebChatComponent;
