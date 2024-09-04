// app.js


// async function uploadVideo() {
//     const videoInput = document.getElementById('videoInput').files[0];
    
//     if (!videoInput) {
//         alert('Please select a video file.');
//         return;
//     }
    
//     const formData = new FormData();
//     formData.append('video', videoInput);

//     try {
//         const response = await fetch('http://localhost:5000/upload', {
//             method: 'POST',
//             body: formData
//         });

//         if (response.ok) {
//             alert('Video uploaded successfully.');
//         } else {
//             alert('Failed to upload video.');
//         }
//     } catch (error) {
//         console.error('Error:', error);
//         alert('Error uploading video.');
//     }
// }

document.addEventListener('DOMContentLoaded', function() {
    const uploadSection = document.getElementById('uploadSection');
    const videoInput = document.getElementById('videoInput');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressContainer = document.getElementById('progressContainer');

    // 当点击 uploadSection 时，触发 videoInput 的点击事件
    uploadSection.addEventListener('click', function() {
        videoInput.click();
    });

    videoInput.addEventListener('change', function() {
        if (videoInput.files.length > 0) {
            // 处理视频上传逻辑
            uploadVideo();
        }
    });

    async function uploadVideo() {
        const videoFile = videoInput.files[0];

        if (!videoFile) {
            alert('Please select a video file.');
            return;
        }

        const formData = new FormData();
        formData.append('video', videoFile);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', 'http:/172.16.108.67:5001/upload', true);

        // 监听上传进度事件
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressBar.value = percentComplete;
                progressText.innerText = `${Math.round(percentComplete)}%`;

                // // 如果上传完成，隐藏进度条
                // if (percentComplete === 100) {
                //     setTimeout(() => {
                //         progressContainer.style.display = 'none';
                //     }, 1000);
                // }
            }
        });

        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                progressContainer.style.display = 'none';
                if (xhr.status === 200) {
                    alert('Video uploaded successfully.');
                } else {
                    let errorMsg = 'Failed to upload video.';
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.error) {
                            errorMsg += ` Error: ${response.error}`;
                        }
                    } catch (e) {
                        // Ignore JSON parse errors
                    }
                    alert(errorMsg);
                }
            }
        };

        xhr.onerror = function() {
            progressContainer.style.display = 'none';
            alert('Error uploading video.');
        }

        // 显示进度条容器并重置进度
        progressContainer.style.display = 'block';
        progressBar.value = 0;
        progressText.innerText = '0%';

        xhr.send(formData);


        // try {
        //     const response = await fetch('http://172.16.108.67:5001/upload', {
        //         method: 'POST',
        //         body: formData
        //     });

        //     if (response.ok) {
        //         alert('Video uploaded successfully.');
        //     } else {
        //         alert('Failed to upload video.');
        //     }
        // } catch (error) {
        //     console.error('Error:', error);
        //     alert('Error uploading video.');
        // }
    }


    document.getElementById('queryBtn').addEventListener('click', queryFrames);
    document.getElementById('voiceBtn').addEventListener('click', queryByVoice);


    async function queryFrames() {
        const query = document.getElementById('queryInput').value;

        if (!query) {
            alert('Please enter a query.');
            return;
        }

        try {
            const response = await fetch('http://172.16.108.67:5001/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });

            if (response.ok) {
                const data = await response.json();

                // 清空之前的结果
                for (let i = 1; i <= 4; i++) {
                    const videoElement = document.getElementById(`resultVideo${i}`);
                    videoElement.src = '';
                    videoElement.load();
                }

                // 设置新的视频源并跳转到指定帧
                for (let i = 0; i < data.length && i < 4; i++) {
                    const videoElement = document.getElementById(`resultVideo${i+1}`);
                    const video_url = data[i].video_url;
                    const frame_time = data[i].frame_time;

                    // 设置视频源
                    videoElement.src = video_url;

                    // 等待视频元数据加载后跳转到指定时间
                    videoElement.addEventListener('loadedmetadata', function() {
                        videoElement.currentTime = frame_time;
                    }, { once: true });
                }
            } else {
                let errorMsg = 'No results found.';
                try {
                    const response = await response.json();
                    if (response.error) {
                        errorMsg = `Query failed. Error: ${response.error}`;
                    }
                } catch (e) {
                    // Ignore JSON parse errors
                }
                alert(errorMsg);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error querying frames.');
        }
    }

    function queryByVoice() {
        alert('Voice query is not yet implemented.');
    }
});


// async function queryFrames() {
//     const query = document.getElementById('queryInput').value;

//     if (!query) {
//         alert('Please enter a query.');
//         return;
//     }

//     try {
//         const response = await fetch('http://172.16.108.67:5001/query', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify({ query })
//         });

//         if (response.ok) {
//             const data = await response.json();
//             document.getElementById('resultFrame').src = data.frame_path;
//             document.getElementById('resultVideo').src = data.video_path;
//         } else {
//             alert('No results found.');
//         }
//     } catch (error) {
//         console.error('Error:', error);
//         alert('Error querying frames.');
//     }
// }

// function queryByVoice() {
//     alert('Voice query is not yet implemented.');
// }


// function setVideoToFrame(videoElement, videoSrc, frameTime) {
//     videoElement.src = videoSrc;
//     videoElement.currentTime = frameTime;
// }

// document.getElementById('queryBtn').addEventListener('click', function() {
//     // Assume these values are dynamically obtained based on the query
//     const videos = ['video1.mp4', 'video2.mp4', 'video3.mp4', 'video4.mp4'];
//     const frameTimes = [10, 20, 30, 40]; // These are the times in seconds

//     for (let i = 1; i <= 4; i++) {
//         const videoElement = document.getElementById(`resultVideo${i}`);
//         setVideoToFrame(videoElement, videos[i-1], frameTimes[i-1]);
//     }
// });
