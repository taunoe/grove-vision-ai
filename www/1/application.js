const WEBUSB_JPEG_MAGIC = 0x2B2D2B2D;
const WEBUSB_TEXT_MAGIC = 0x0F100E12;
const ALGO_OBJECT_DETECTION = 0x00;
const ALGO_OBJECT_COUNT = 0x01;
const ALGO_IMAGE_CLASSIFICATION = 0x02;
const MODEL_PRE_INDEX_1 = 0x00;

const MODEL_PRE_INDEX_1_TARGET_0 = 'Noting';
const MODEL_PRE_INDEX_1_TARGET_1 = 'Panda';
const MODEL_PRE_INDEX_1_TARGET_2 = 'Person';

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', event => {
        let connectButton = document.querySelector("#connect");
        let statusDisplay = document.querySelector('#status');
        let port;

        function concatenate(resultConstructor, ...arrays) {
            let totalLength = 0;
            for (let arr of arrays) {
                totalLength += arr.length;
            }
            let result = new resultConstructor(totalLength);
            let offset = 0;
            for (let arr of arrays) {
                result.set(arr, offset);
                offset += arr.length;
            }
            return result;
        }

        function Uint8ArrayToString(u8Arr) {
            var dataString = "";
            for (var i = 0; i < u8Arr.length; i++) {
                dataString += String.fromCharCode(u8Arr[i]);
            }
            return dataString
        }

        function uint8arrayToBase64(u8Arr) {
            let CHUNK_SIZE = 0x8000; //arbitrary number
            let index = 0;
            let length = u8Arr.length;
            let result = '';
            let slice;
            while (index < length) {
                slice = u8Arr.subarray(index, Math.min(index + CHUNK_SIZE, length));
                result += String.fromCharCode.apply(null, slice);
                index += CHUNK_SIZE;
            }
            // web image base64: "data:image/png;base64," + b64encoded;
            // return  "data:image/png;base64," + btoa(result);
            return btoa(result);
        }

        var data_buffer = new Uint8Array(0);
        var status = 0;
        var recv_size = 0;
        var execpt_size = 0;

        function connect() {
            port.connect().then(() => {
                statusDisplay.textContent = '';
                connectButton.textContent = 'Disconnect';

                document.getElementById("loading").innerHTML = "";

                port.onReceive = data => {
                    if (data.byteLength == 8 && data.getUint32(0) == WEBUSB_JPEG_MAGIC) {
                        recv_size = 0;
                        status = 0;
                        execpt_size = parseInt(data.getUint32(4));
                        data_buffer = new Uint8Array(0);
                    } else if (data.byteLength == 8 && data.getUint32(0) == WEBUSB_TEXT_MAGIC) {
                        recv_size = 0;
                        status = 1;
                        execpt_size = parseInt(data.getUint32(4));
                        data_buffer = new Uint8Array(0);
                    }
                    else {
                        data_buffer = concatenate(Uint8Array, data_buffer, new Uint8Array(data.buffer));
                        recv_size += data.byteLength;
                    }

                    if (recv_size == execpt_size) {
                        recv_size = 0;
                        if (status == 0) {
                            var str = uint8arrayToBase64(data_buffer);
                            var canvas = document.getElementById("myCavans");
                            var outdiv = document.getElementById("outdiv");
                            var ctx = canvas.getContext("2d");
                            var img = new Image();
                            img.src = 'data:image/jpeg;base64,' + str;
                            img.onload = function () {
                                let width = this.naturalWidth;
                                let height = this.naturalHeight;
                                canvas.width = width
                                canvas.height = height;
                                ctx.translate(canvas.width * 0.5, canvas.height * 0.5);
                                ctx.rotate(-1* Math.PI/2);
                                ctx.drawImage(img, - canvas.width / 2, - canvas.height / 2, canvas.width, canvas.height);
                            }
                        } else {
                            var str = '' + Uint8ArrayToString(data_buffer);
                            var canvas = document.getElementById("myCavans");
                            var ctx = canvas.getContext("2d");
                            ctx.translate(96, -96);
                            ctx.rotate(1* Math.PI/2);
                            ctx.strokeStyle = "#f00";
                            ctx.fillStyle = "#0f0";
                            try {
                                var obj = JSON.parse(str);
                                if (obj != null) {
                                    console.log(obj);
                                    if (obj.type == "preview") {
                                        if (obj.algorithm == ALGO_OBJECT_DETECTION) {
                                            for (var i = 0; i < obj.count; i++) {
                                                ctx.font = "bold 16px arial";
                                                ctx.fillText(obj.object.target[i], obj.object.x[i], obj.object.y[i]);
                                                ctx.fillText(obj.object.confidence[i], obj.object.x[i] + 30, obj.object.y[i]);
                                                ctx.strokeRect(obj.object.x[i] - obj.object.w[i] / 2, obj.object.y[i] - obj.object.h[i] / 2, obj.object.w[i], obj.object.h[i]);
                                            }
                                        } else if (obj.algorithm == ALGO_IMAGE_CLASSIFICATION) {

                                            for (var i = 0; i < obj.count; i++) {
                                                ctx.font = "bold 16px arial";
                                                if (obj.model == MODEL_PRE_INDEX_1) {
                                                    switch (obj.object.target[i]) {
                                                        case 0x00:
                                                            ctx.fillText(MODEL_PRE_INDEX_1_TARGET_0, 20, 40);
                                                            break;
                                                        case 0x01:
                                                            ctx.fillText(MODEL_PRE_INDEX_1_TARGET_1, 20, 40);
                                                            break;
                                                        case 0x02:
                                                            ctx.fillText(MODEL_PRE_INDEX_1_TARGET_2, 20, 40);
                                                            break;
                                                    }
                                                } else {
                                                    ctx.fillText(obj.object.target[i], 20, 40);
                                                }

                                                ctx.fillText(obj.object.confidence[i], 20, 60);
                                            }
                                        }
                                    }
                                }
                            } catch (error) {
                                console.log(error.message);
                            }
                        }
                    }
                };
                port.onReceiveError = error => {
                    console.error(error);
                };
            }, error => {
                statusDisplay.textContent = error;
            });
        }

        connectButton.addEventListener('click', function () {
            if (port) {
                port.disconnect();
                connectButton.textContent = 'Connect';
                statusDisplay.textContent = '';
                port = null;
                document.getElementById("loading").innerHTML = "<div class=\"double-bounce1\"></div><div class=\"double-bounce2\"></div>"
            } else {
                serial.requestPort().then(selectedPort => {
                    port = selectedPort;
                    connect();
                }).catch(error => {
                    statusDisplay.textContent = error;
                });
            }
        });

        serial.getPorts().then(ports => {
            if (ports.length === 0) {
                statusDisplay.textContent = 'No device found.';
            } else {
                statusDisplay.textContent = 'Connecting...';
                port = ports[0];
                connect();
            }
        });
    });
})();