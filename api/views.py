from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView


class BindWechatView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        openid = request.data.get('openId')
        if openid is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        from wechat.utils import bind_wechat
        bind_wechat(request.user, openid)

        return Response({'msg': '恭喜您成功绑定了「学导有约」平台的账号。'})
